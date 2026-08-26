import hmac
import hashlib
import time
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client

from bot.config import (
    BOT_TOKEN,
    SUPABASE_URL,
    SUPABASE_KEY,
    WAYFORPAY_SECRET_KEY,
)
from bot.services.wayforpay import verify_callback_signature, create_payment_link

logging.basicConfig(level=logging.INFO)

# Параметри продукту з оточення (з дефолтними значеннями)
PRODUCT_PRICE = float(os.getenv("PRODUCT_PRICE", "100.0"))
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Доступ до матеріалів")

# Ініціалізація клієнтів
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Хендлери Telegram Бота ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обробка /start та створення/оновлення користувача в БД."""
    user_id = message.from_user.id

    try:
        supabase.table("users").upsert(
            {
                "telegram_id": user_id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
            },
            on_conflict="telegram_id",
        ).execute()
    except Exception as e:
        logging.error(f"Помилка створення користувача в Supabase: {e}")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💳 Придбати доступ ({PRODUCT_PRICE:.0f} UAH)",
                    callback_data="buy_access",
                )
            ]
        ]
    )
    await message.answer(
        "Привіт! Натисни кнопку нижче, щоб оформити замовлення:",
        reply_markup=kb,
    )


@dp.callback_query(lambda c: c.data == "buy_access")
async def process_buy(callback: types.CallbackQuery):
    """Формування замовлення та видача посилання на оплату."""
    user_id = callback.from_user.id
    order_id = f"pay_{user_id}_{int(time.time())}"

    try:
        # Запис замовлення зі статусом pending
        supabase.table("orders").insert(
            {
                "order_id": order_id,
                "telegram_id": user_id,
                "amount": PRODUCT_PRICE,
                "status": "pending",
            }
        ).execute()
    except Exception as e:
        logging.error(f"Помилка створення замовлення в Supabase: {e}")
        await callback.answer("⚠️ Помилка створення замовлення. Спробуйте пізніше.", show_alert=True)
        return

    payment_url = create_payment_link(
        order_id=order_id,
        amount=PRODUCT_PRICE,
        product_name=PRODUCT_NAME,
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Перейти до оплати WayForPay", url=payment_url)]
        ]
    )
    await callback.message.answer(
        f"Ваше замовлення `{order_id}` сформовано.\n"
        f"Сума до сплати: **{PRODUCT_PRICE:.2f} UAH**",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await callback.answer()


# --- Lifespan: Керування фоновим ботом разом із FastAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаємо polling бота в окремій асинхронній тасці
    polling_task = asyncio.create_task(dp.start_polling(bot))
    logging.info("🚀 Telegram-бот успішно запущений у фоновому режимі")
    
    yield
    
    # Зупинка бота під час вимкнення сервера
    polling_task.cancel()
    await bot.session.close()
    logging.info("🛑 Сервер та Telegram-бот зупинені")


app = FastAPI(lifespan=lifespan)


# --- Роут для вебхука WayForPay ---

@app.post("/payment/callback")
async def payment_callback(request: Request):
    """
    Приймає та перевіряє сповіщення про статус оплати від WayForPay.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # 1. Валідація HMAC-підпису
    if not verify_callback_signature(data):
        logging.warning("⚠️ Отримано вебхук з недійсним підписом!")
        raise HTTPException(status_code=400, detail="Invalid signature")

    status = data.get("transactionStatus")
    order_id = data.get("orderReference")

    if status == "Approved":
        try:
            # Отримуємо замовлення з бази
            order_res = (
                supabase.table("orders")
                .select("*")
                .eq("order_id", order_id)
                .execute()
            )

            if order_res.data:
                order = order_res.data[0]
                telegram_id = order["telegram_id"]

                # Перевіряємо, чи не було замовлення вже оброблено раніше
                if order.get("status") != "paid":
                    # 2. Оновлюємо статус замовлення
                    supabase.table("orders").update({"status": "paid"}).eq(
                        "order_id", order_id
                    ).execute()

                    # 3. Надаємо доступ користувачу
                    supabase.table("users").update({"has_access": True}).eq(
                        "telegram_id", telegram_id
                    ).execute()

                    # 4. Сповіщаємо користувача в Telegram
                    try:
                        await bot.send_message(
                            chat_id=telegram_id,
                            text="🎉 **Оплату успішно підтверджено!**\nВаш доступ активовано.",
                            parse_mode="Markdown",
                        )
                    except Exception as send_err:
                        logging.error(
                            f"Не вдалося надіслати сповіщення юзеру {telegram_id}: {send_err}"
                        )

        except Exception as db_err:
            logging.error(f"Помилка при обробці бази даних у колбеку: {db_err}")
            raise HTTPException(status_code=500, detail="Database error")

        # 5. Генеруємо відповідь-підтвердження для WayForPay (строго за специфікацією)
        time_now = int(time.time())
        sign_str = f"{order_id};ACCEPT;{time_now}"
        response_signature = hmac.new(
            WAYFORPAY_SECRET_KEY.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.md5,
        ).hexdigest()

        return {
            "orderReference": order_id,
            "status": "ACCEPT",
            "time": time_now,
            "signature": response_signature,
        }

    return {"status": "ignored"}
