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

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    
    # Витягуємо реферала, якщо він перейшов за посиланням /start <ref_id>
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    referrer_id = int(args[0]) if args and args[0].isdigit() else None
    
    try:
        await DBClient.get_or_create_user(
            user_id=user_id, 
            username=username, 
            first_name=first_name, 
            referrer_id=referrer_id
        )
    except Exception as e:
        logger.error(f"Помилка створення користувача: {e}")

    is_admin = user_id in ADMIN_IDS
    text = (
        f"Вітаю, **{first_name}**! 👋\n\n"
        f"Це твій персональний тренажер підготовки до **НМТ з англійської мови**.\n"
        f"Тут ти зможеш прокачати граматику, уникнути типових пасток та скласти іспит на **190+**!\n\n"
        f"Обирай дію в меню:"
    )
    
    await message.answer(
        text,
        reply_markup=get_main_keyboard(web_app_url=WEB_APP_URL, is_admin=is_admin),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: CallbackQuery):
    await callback.answer()
    is_admin = callback.from_user.id in ADMIN_IDS
    await callback.message.edit_text(
        "📍 **Головне меню:**",
        reply_markup=get_main_keyboard(web_app_url=WEB_APP_URL, is_admin=is_admin),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "show_profile")
async def cb_show_profile(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    user_data = await DBClient.get_or_create_user(
        user_id=user_id, 
        username=callback.from_user.username, 
        first_name=callback.from_user.first_name
    )

    streak = user_data.get("streak", 1)
    xp = user_data.get("xp", 0)
    referrals = user_data.get("referrals_count", 0)
    is_premium = user_data.get("is_premium", False)
    
    status = "👑 **Premium Користувач**" if is_premium else "👤 **Базовий акаунт**"
    
    profile_text = (
        f"👤 **Твій Профіль Навчання**\n\n"
        f"Статус: {status}\n"
        f"🔥 Щоденний стрик: **{streak} днів**\n"
        f"⚡ Зароблений досвід: **{xp} XP**\n"
        f"👥 Запрошено друзів: **{referrals}**\n\n"
        f"💡 *Порада: Кожні 2 запрошені друга відкривають тобі Premium безкоштовно!*"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "show_tariffs")
async def cb_show_tariffs(callback: CallbackQuery):
    await callback.answer()
    
    # Психологічно переконуючий текст (орієнтований на абітурієнтів та батьків)
    tariffs_text = (
        f"🎯 **Твій впевнений крок до 190+ на НМТ!**\n\n"
        f"Більшість втрачає бали не через незнання мови, а через пастки у форматах завдань. "
        f"Ми розробили систему, яка гарантує результат:\n\n"
        f"✨ **Преміум-доступ у боті:**\n"
        f"• Повні авторські розбори кожної помилки\n"
        f"• Симулятор завдань підвищеної складності (B2)\n"
        f"• Особистий трекінг слабких тем\n\n"
        f"🏛 **Школа Neta School (Повний курс):**\n"
        f"• Індивідуальна програма та супровід ментора\n"
        f"• Повна гарантія вступу на омріяний бюджет\n\n"
        f"👇 **Обери зручний спосіб оплати або вступу:**"
    )
    
    await callback.message.edit_text(
        tariffs_text,
        reply_markup=get_tariffs_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "start_quiz_menu")
async def cb_start_quiz_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🧠 **Обери рівень складності тренування:**",
        reply_markup=get_difficulty_keyboard(),
        parse_mode="Markdown"
    )

# --- АДМІН ПАНЕЛЬТА СТАТИСТИКА ---

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("⚡ **Панель адміністратора**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(callback: CallbackQuery):
    await callback.answer()
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("⚡ **Панель адміністратора**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    await callback.answer()
    if callback.from_user.id not in ADMIN_IDS:
        return
        
    stats = await DBClient.get_admin_stats()
    
    stats_text = (
        f"📊 **Точна статистика проекту:**\n\n"
        f"👥 Всього користувачів: **{stats['total_users']}**\n"
        f"👑 З активним Premium: **{stats['premium_users']}**\n"
        f"📚 Питань у базі даних: **{stats['total_questions']}**"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_keyboard(),
        parse_mode="Markdown"
    )
