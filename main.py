import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot.handlers import router
from bot.middlewares import AntiSpamMiddleware
from bot.db_client import DBClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

# Ендпоінт для пінгу сервісу (Render, UptimeRobot тощо)
async def handle_ping(request):
    return web.Response(text="NMT Bot Service Active 🚀", status=200)

async def start_healthcheck():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"HTTP Server runs on port {port}")

async def main():
    dp = Dispatcher(storage=MemoryStorage())
    
    # Реєстрація AntiSpam Middleware
    antispam_middleware = AntiSpamMiddleware(limit=0.7)
    dp.message.middleware(antispam_middleware)
    dp.callback_query.middleware(antispam_middleware)

    # Підключення роутера з хендлерами
    dp.include_router(router)

    # Глобальний обробник помилок
    @dp.error()
    async def global_error_handler(event):
        logger.error(f"Глобальне перехоплення помилки: {event.exception}", exc_info=True)
        return True

    # Запуск HTTP сервера для пінгу та поллінгу бота
    await start_healthcheck()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
