import asyncio
import logging
import os
from contextlib import suppress

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from bot.admin import admin_router
from bot.config import (
    PORT,
    RETENTION_CHECK_INTERVAL_SECONDS,
    RETENTION_INACTIVE_HOURS,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
    get_webhook_url,
)
from bot.db_client import DBClient
from bot.handlers import router as main_router
from bot.keyboards import get_retention_answer_keyboard
from bot.middlewares import AntiSpamMiddleware


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger(__name__)


bot = Bot(
    token=os.environ["BOT_TOKEN"],
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


async def health(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "status": "ok",
            "service": "nmt-english-bot",
        }
    )


async def retention_loop() -> None:
    """
    Перевіряє користувачів раз на годину.

    У разі відсутності понад 24 години надсилає одне питання.
    """

    await asyncio.sleep(30)

    while True:
        try:
            candidates = await DBClient.get_retention_candidates(
                limit=100,
            )

            logger.info(
                "Retention scan: %s candidates",
                len(candidates),
            )

            for user in candidates:
                user_id = int(user["user_id"])

                try:
                    tasks = await DBClient.get_personalized_tasks(
                        user_id=user_id,
                        category="personalized",
                        limit=1,
                    )

                    if not tasks:
                        continue

                    task = tasks[0]

                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            "🔥 <b>Твій Streak чекає</b>\n\n"
                            "Ось одне коротке питання. "
                            "Перевір себе:"
                            "\n\n"
                            f"{task.get('question_text', '')}"
                        ),
                        reply_markup=get_retention_answer_keyboard(
                            task_id=int(task["id"]),
                            options=task.get("options") or {},
                        ),
                    )

                    await DBClient.set_last_reminder(
                        user_id,
                    )

                    # Додаткова пауза між Telegram API викликами.
                    await asyncio.sleep(0.05)

                except Exception as exc:
                    logger.warning(
                        "Retention failed for %s: %s",
                        user_id,
                        exc,
                    )

        except Exception as exc:
            logger.exception(
                "Retention loop error: %s",
                exc,
            )

        await asyncio.sleep(
            RETENTION_CHECK_INTERVAL_SECONDS
        )


async def retention_answer(
    callback,
) -> None:
    """
    Реєструється в окремому router нижче.
    Функція тут не використовується напряму.
    """
    return None


async def on_startup(
    dispatcher: Dispatcher,
) -> None:
    webhook_url = get_webhook_url()

    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=dispatcher.resolve_used_update_types(),
        max_connections=20,
    )

    logger.info(
        "Webhook configured: %s",
        webhook_url,
    )


async def on_shutdown(
    dispatcher: Dispatcher,
) -> None:
    retention_task = dispatcher["retention_task"]

    retention_task.cancel()

    with suppress(asyncio.CancelledError):
        await retention_task

    await bot.delete_webhook()

    await bot.session.close()

    logger.info("Bot stopped.")


async def create_application() -> web.Application:
    dp = Dispatcher(
        storage=MemoryStorage(),
    )

    anti_spam = AntiSpamMiddleware(
        limit=0.7,
    )

    dp.message.middleware(anti_spam)
    dp.callback_query.middleware(anti_spam)

    # Адмінський router ПЕРШИМ.
    dp.include_router(admin_router)
    dp.include_router(main_router)

    # Retention callback router.
    from aiogram import Router, F
    from aiogram.types import CallbackQuery

    retention_router = Router()

    @retention_router.callback_query(
        F.data.startswith("retention_answer:")
    )
    async def handle_retention_answer(
        callback: CallbackQuery,
    ) -> None:
        parts = callback.data.split(":")

        if len(parts) != 3:
            await callback.answer(
                "Некоректна відповідь.",
                show_alert=True,
            )
            return

        try:
            task_id = int(parts[1])
        except ValueError:
            await callback.answer(
                "Некоректне питання.",
                show_alert=True,
            )
            return

        answer = parts[2].upper()

        if answer not in {"A", "B", "C", "D"}:
            await callback.answer(
                "Некоректна відповідь.",
                show_alert=True,
            )
            return

        # Беремо питання через персоналізований пошук.
        tasks = await DBClient.get_personalized_tasks(
            user_id=callback.from_user.id,
            category="personalized",
            limit=50,
        )

        task = next(
            (
                item
                for item in tasks
                if int(item["id"]) == task_id
            ),
            None,
        )

        if task is None:
            await callback.answer(
                "Питання вже неактивне.",
                show_alert=True,
            )
            return

        correct = (
            str(task.get("correct_answer", "")).upper()
        )

        is_correct = answer == correct

        await DBClient.save_attempt(
            user_id=callback.from_user.id,
            task_id=task_id,
            answer=answer,
            is_correct=is_correct,
        )

        await callback.answer(
            "🔥 Streak продовжено!" if is_correct else "❌ Є над чим попрацювати."
        )

        if is_correct:
            text = (
                "🔥 <b>Правильно!</b>\n\n"
                "Ще один день у грі."
            )
        else:
            text = (
                "💡 <b>Це була пастка.</b>\n\n"
                f"{task.get('explanation') or 'Збережено у твоїх помилках.'}"
            )

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
        )

    dp.include_router(retention_router)

    retention_task = asyncio.create_task(
        retention_loop(),
        name="retention-loop",
    )

    dp["retention_task"] = retention_task

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    @dp.error()
    async def global_error_handler(event) -> bool:
        logger.exception(
            "Unhandled update error: %s",
            event.exception,
        )
        return True

    app = web.Application()

    app.router.add_get(
        "/",
        health,
    )

    app.router.add_get(
        "/health",
        health,
    )

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
        handle_in_background=True,
    )

    webhook_handler.register(
        app,
        path=WEBHOOK_PATH,
    )

    setup_application(
        app,
        dp,
        bot=bot,
    )

    return app


async def main() -> None:
    app = await create_application()

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT,
    )

    await site.start()

    logger.info(
        "HTTP server started on 0.0.0.0:%s",
        PORT,
    )

    try:
        while True:
            await asyncio.sleep(3600)

    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
