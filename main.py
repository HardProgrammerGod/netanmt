# main.py
import os
import time
import hmac
import hashlib
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, ADMIN_IDS, WAYFORPAY_SECRET_KEY
from bot.handlers import router
from bot.middlewares import AntiSpamMiddleware
from bot.db_client import DBClient
from bot.payments import verify_wayforpay_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

# --- Webhook для прийому платежів від WayForPay ---
async def handle_wayforpay_callback(request):
    try:
        data = await request.json()
        logger.info(f"Отримано сповіщення від WayForPay: {data}")

        if verify_wayforpay_response(data):
            if data.get("transactionStatus") == "Approved":
                order_ref = data.get("orderReference", "") # order_123456789_month_1700000000
                parts = order_ref.split("_")
                
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    plan_type = parts[2]
                    
                    # Активуємо Premium в БД
                    DBClient.set_premium(user_id)
                    
                    # Повідомляємо юзера в Telegram
                    try:
                        await bot.send_message(
                            user_id, 
                            "🎉 **Дякуємо за оплату!**\n\nВаш **Premium-доступ** успішно активовано. Всі обмеження знято, приємного навчання!",
                            parse_mode="Markdown"
                        )
                    except Exception as send_err:
                        logger.error(f"Не вдалося надіслати повідомлення юзеру {user_id}: {send_err}")

                # Формуємо відповідь для WayForPay
                time_stamp = int(time.time())
                sign_str = f"{order_ref};accept;{time_stamp}"
                sign = hmac.new(WAYFORPAY_SECRET_KEY.encode('utf-8'), sign_str.encode('utf-8'), hashlib.md5).hexdigest()
                
                response_data = {
                    "orderReference": order_ref,
                    "status": "accept",
                    "time": time_stamp,
                    "signature": sign
                }
                return web.json_response(response_data)

        return web.json_response({"status": "error", "message": "Invalid signature"}, status=400)
    except Exception as e:
        logger.error(f"Помилка обробки WayForPay callback: {e}")
        return web.json_response({"status": "error"}, status=500)

async def handle_ping(request):
    return web.Response(text="NMT Bot Service Active 🚀", status=200)

async def start_healthcheck():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    app.router.add_post("/wayforpay/callback", handle_wayforpay_callback)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"HTTP Server runs on port {port}")

async def main():
    dp = Dispatcher(storage=MemoryStorage())
    
    antispam_middleware = AntiSpamMiddleware(limit=0.7)
    dp.message.middleware(antispam_middleware)
    dp.callback_query.middleware(antispam_middleware)

    dp.include_router(router)

    @dp.error()
    async def global_error_handler(event):
        logger.error(f"Глобальне перехоплення помилки: {event.exception}", exc_info=True)
        return True

    await start_healthcheck()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
