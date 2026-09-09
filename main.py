import asyncio
import logging
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
    BOT_TOKEN,
    PORT,
    WEBHOOK_PATH,
    WEBHOOK_URL,
)
from bot.handlers import (
    daily_retention_loop,
    router as main_router,
)
from bot.middlewares import AntiSpamMiddleware


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

dp = Dispatcher(
    storage=MemoryStorage()
)


# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------

anti_spam = AntiSpamMiddleware(
    limit=0.7,
    max_users=5000,
)

dp.message.middleware(
    anti_spam
)

dp.callback_query.middleware(
    anti_spam
)


# ------------------------------------------------------------
# Routers
# Admin MUST be first.
# ------------------------------------------------------------

dp.include_router(
    admin_router
)

dp.include_router(
    main_router
)


# ------------------------------------------------------------
# Global error handler
# ------------------------------------------------------------

@dp.error()
async def global_error_handler(
    event,
):
    logger.exception(
        "Unhandled Telegram update error: %s",
        event.exception,
    )

    return True


# ------------------------------------------------------------
# Health
# ------------------------------------------------------------

async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "status": "ok",
            "service": "nmt-english-bot",
        }
    )


async def root_handler(
    request: web.Request,
) -> web.Response:

    return web.Response(
        text="NMT English Bot is running.",
        status=200,
    )


# ------------------------------------------------------------
# Startup
# ------------------------------------------------------------

async def on_startup(
    app: web.Application,
):

    logger.info(
        "🚀 Starting NMT English Bot..."
    )

    logger.info(
        "Webhook URL: %s",
        WEBHOOK_URL,
    )

    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=False,
    )

    retention_task = asyncio.create_task(
        daily_retention_loop(bot),
        name="daily-retention-loop",
    )

    app["retention_task"] = retention_task

    logger.info(
        "✅ Telegram webhook configured."
    )


# ------------------------------------------------------------
# Shutdown
# ------------------------------------------------------------

async def on_shutdown(
    app: web.Application,
):

    logger.info(
        "🛑 Shutting down..."
    )

    retention_task = app.get(
        "retention_task"
    )

    if retention_task:
        retention_task.cancel()

        with suppress(
            asyncio.CancelledError
        ):
            await retention_task

    with suppress(Exception):
        await bot.session.close()

    logger.info(
        "✅ Shutdown complete."
    )


# ------------------------------------------------------------
# App
# ------------------------------------------------------------

app = web.Application(
    client_max_size=1024 * 1024
)

app.router.add_get(
    "/",
    root_handler,
)

app.router.add_get(
    "/health",
    health_handler,
)

SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
).register(
    app,
    path=WEBHOOK_PATH,
)

setup_application(
    app,
    dp,
    bot=bot,
)

app.on_startup.append(
    on_startup
)

app.on_shutdown.append(
    on_shutdown
)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

def main():

    logger.info(
        "🌐 HTTP server starting on port %s",
        PORT,
    )

    web.run_app(
        app,
        host="0.0.0.0",
        port=PORT,
    )


if __name__ == "__main__":
    main()
