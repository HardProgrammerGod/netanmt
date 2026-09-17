import asyncio
import logging
import time
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
    WEBHOOK_SECRET,
)
from bot.handlers import (
    daily_retention_loop,
    router as main_router,
)
from bot.middlewares import AntiSpamMiddleware
from bot.learning_db import LearningDB


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
PROCESS_STARTED = time.perf_counter()
FIRST_WEBHOOK_SEEN = False


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
# HTTP latency / cold-start measurement
# ------------------------------------------------------------

@web.middleware
async def latency_middleware(request: web.Request, handler):
    global FIRST_WEBHOOK_SEEN
    started = time.perf_counter()
    response = await handler(request)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    if request.path == WEBHOOK_PATH:
        asyncio.create_task(LearningDB.record_metric("webhook_response_ms", elapsed_ms))
        if not FIRST_WEBHOOK_SEEN:
            FIRST_WEBHOOK_SEEN = True
            cold_ms = round((time.perf_counter() - PROCESS_STARTED) * 1000)
            asyncio.create_task(LearningDB.record_metric("process_to_first_webhook_ms", cold_ms))
            logger.info("First webhook after process start: %sms", cold_ms)
    return response


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
        secret_token=WEBHOOK_SECRET,
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
    client_max_size=1024 * 1024,
    middlewares=[latency_middleware],
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
    secret_token=WEBHOOK_SECRET,
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
