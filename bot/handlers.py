import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot.config import ADMIN_IDS, WEB_APP_URL
from bot.db_client import DBClient
from bot.keyboards import (
    get_main_keyboard,
    get_profile_keyboard,
    get_tariffs_keyboard,
    get_difficulty_keyboard,
    get_admin_keyboard
)

logger = logging.getLogger(__name__)
router = Router()
db = DBClient()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Оновлюємо або створюємо користувача в БД
    try:
        await db.get_or_create_user(user_id=user_id, username=username)
    except Exception as e:
        logger.error(f"Помилка створення користувача в БД: {e}")

    is_admin = user_id in ADMIN_IDS
    text = (
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        f"Ласкаво просимо до інтерактивного тренажера підготовки до **НМТ з англійської мови**!\n\n"
        f"Обирай розділ у меню нижче:"
    )
    
    await message.answer(
        text,
        reply_markup=get_main_keyboard(web_app_url=WEB_APP_URL, is_admin=is_admin),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    is_admin = user_id in ADMIN_IDS
    
    text = "Головне меню:"
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_main_keyboard(web_app_url=WEB_APP_URL, is_admin=is_admin)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=get_main_keyboard(web_app_url=WEB_APP_URL, is_admin=is_admin)
        )

@router.callback_query(F.data == "show_profile")
async def cb_show_profile(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    try:
        user_data = await db.get_or_create_user(user_id=user_id, username=username)
    except Exception as e:
        logger.error(f"Помилка зчитування профілю: {e}")
        user_data = {}

    streak = user_data.get("streak", 0)
    xp = user_data.get("xp", 0)
    is_premium = user_data.get("is_premium", False)
    
    status = "👑 Premium Користувач" if is_premium else "👤 Базовий акаунт"
    
    profile_text = (
        f"👤 **Твій Профіль**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"🔥 Стрік днів: **{streak}**\n"
        f"⚡ Досвід (XP): **{xp}**\n"
        f"Статус: {status}\n\n"
        f"Продовжуй щоденні тренування, щоб покращувати свій стрик!"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "show_tariffs")
async def cb_show_tariffs(callback: CallbackQuery):
    await callback.answer()
    
    tariffs_text = (
        f"👑 **Преміум доступ & Neta School**\n\n"
        f"Підключи Premium, щоб отримати доступ до:\n"
        f"• Повних пояснень відповідей від викладачів\n"
        f"• Симулятора складних завдань рівня B2 (190+)\n"
        f"• Персональної аналітики помилок\n\n"
        f"Обери потрібний варіант нижче:"
    )
    
    await callback.message.edit_text(
        tariffs_text,
        reply_markup=get_tariffs_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "start_quiz_menu")
async def cb_start_quiz_menu(callback: CallbackQuery):
    await callback.answer()
    
    text = "🎯 **Обери рівень складності тестів:**"
    await callback.message.edit_text(
        text,
        reply_markup=get_difficulty_keyboard(),
        parse_mode="Markdown"
    )

# --- АДМІН ПАНЕЛЬ ---

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
        
    await message.answer(
        "⚡ **Панель адміністратора**",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(callback: CallbackQuery):
    await callback.answer()
    if callback.from_user.id not in ADMIN_IDS:
        return
        
    await callback.message.edit_text(
        "⚡ **Панель адміністратора**",
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    await callback.answer()
    if callback.from_user.id not in ADMIN_IDS:
        return
        
    total_users = await db.get_users_count()
    
    stats_text = (
        f"📊 **Статистика бота:**\n\n"
        f"👥 Всього користувачів у БД: **{total_users}**"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )
