from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_USERNAME

def get_main_keyboard(web_app_url: str = None, is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🚀 Розпочати тест (Duolingo Style)", callback_data="start_quiz_menu")
    builder.button(text="🔥 Мій Стрік & Профіль", callback_data="show_profile")
    builder.button(text="🎁 Запросити друга (+Premium)", callback_data="show_referral")
    builder.button(text="👑 Premium / Школа NMT", callback_data="show_tariffs")
    
    if web_app_url:
        builder.button(text="🌐 Навчальна Платформа (WebApp)", web_app=WebAppInfo(url=web_app_url))
        
    if is_admin:
        builder.button(text="⚡ Адмін Панель", callback_data="admin_panel")

    builder.adjust(1)
    return builder.as_markup()

def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 До тестів", callback_data="start_quiz_menu")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Готуємо тексти повідомлень для адміна
    prem_text = quote("Привіт! Хочу придбати Premium доступ у боті НМТ 🚀")
    school_text = quote("Доброго дня! Хочу дізнатися деталі та вступити на підготовку до Neta School 🎓")
    
    link_premium = f"https://t.me/{ADMIN_USERNAME}?text={prem_text}"
    link_school = f"https://t.me/{ADMIN_USERNAME}?text={school_text}"
    
    builder.button(text="💳 Карта (-27% знижка)", url=link_premium)
    builder.button(text="⭐ 250 Telegram Stars", callback_data="buy_premium_stars")
    builder.button(text="🎓 Навчання в Neta School (Вступ)", url=link_school)
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    
    builder.adjust(1)
    return builder.as_markup()

def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Рівень 1: Розігрів (A1-A2)", callback_data="quiz_diff_1")
    builder.button(text="🟡 Рівень 2: Пастки НМТ (B1)", callback_data="quiz_diff_2")
    builder.button(text="🔴 Рівень 3: Хардкор 190+ (B2)", callback_data="quiz_diff_3")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Точна статистика", callback_data="admin_stats")
    builder.button(text="🔍 Перевірити активних (Audit)", callback_data="admin_check_active")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()
