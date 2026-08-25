import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.admin import admin_router
from bot.handlers import router

logging.basicConfig(level=logging.INFO)

# Крошечный HTTP-сервер для UptimeRobot
async def handle_ping(request):
    return web.Response(text="netaNMT Bot is alive 🚀")

async def start_healthcheck_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Health-check сервер запущен на порту {port}")

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден!")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(router)

    # Запускаем пинг-сервер параллельно с ботом
    await start_healthcheck_server()

    print("🚀 Бот netaNMT успешно запущен в режиме Long Polling!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
