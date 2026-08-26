import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot.handlers import router
from bot.middlewares import AntiSpamMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- HTTP Сервер для Uptime-перевірок на Render (24/7) ---
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
    logger.info(f"Healthcheck HTTP server running on port {port}")

# --- Запуск Бота ---
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Підключаємо захист від спаму кліками
    antispam_middleware = AntiSpamMiddleware(limit=0.7)
    dp.message.middleware(antispam_middleware)
    dp.callback_query.middleware(antispam_middleware)

    dp.include_router(router)

    # Непадучий глобальний обробник помилок
    @dp.error()
    async def global_error_handler(event):
        logger.error(f"Глобальне перехоплення помилки: {event.exception}", exc_info=True)
        return True

    # Запускаємо сервер для веб-сервісу
    await start_healthcheck()
    
    # Сповіщення адмінів про перезапуск
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "🚀 **Бот успішно запущений та готов до роботи!**", parse_mode="Markdown")
        except Exception:
            pass

    logger.info("Бот запущений у режимі Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
