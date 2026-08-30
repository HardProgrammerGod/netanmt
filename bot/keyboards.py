from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_USERNAME


def get_main_keyboard(web_app_url: str = None, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Головне меню бота."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🚀 Розпочати тест НМТ", callback_data="start_quiz_menu")
    builder.button(text="🔥 Мій Стрік & Профіль", callback_data="show_profile")
    builder.button(text="🎁 Запросити друга (+Premium)", callback_data="show_referral")
    builder.button(text="👑 ТВІЙ ШАНС!", callback_data="show_tariffs")
    
    if web_app_url:
        builder.button(text="🌐 Навчальна Платформа (WebApp)", web_app=WebAppInfo(url=web_app_url))
        
    if is_admin:
        builder.button(text="⚡ Адмін Панель", callback_data="admin_panel")

    builder.adjust(1)
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура профілю користувача."""
    builder.button(text="🚀 До тестів НМТ", callback_data="start_quiz_menu")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура вибору тарифів та способів оплати."""
    builder = InlineKeyboardBuilder()
    
    # Тексти звернення в Telegram до адміна
    prem_text = quote("Привіт! Хочу придбати Premium доступ у боті НМТ 🚀")
    school_text = quote("Доброго дня! Хочу дізнатися деталі та вступити на підготовку до Neta School 🎓")
    
    link_premium = f"https://t.me/{ADMIN_USERNAME}?text={prem_text}"
    link_school = f"https://t.me/{ADMIN_USERNAME}?text={school_text}"
    
    builder.button(text="💳 Картка / Менеджер (-27% знижка)", url=link_premium)
    builder.button(text="⭐ 250 Telegram Stars (Автоматично)", callback_data="buy_premium_stars")
    builder.button(text="🎓 Навчання в Neta School (Вступ)", url=link_school)
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    
    builder.adjust(1)
    return builder.as_markup()


def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    """
    Клавіатура вибору тренування НМТ.
    Повністю прибрано шкалу A1-B2 — вибір здійснюється за офіційними блоками НМТ з англійської.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Reading (Читання та тексти)", callback_data="quiz_cat_reading")
    builder.button(text="🔤 Use of English (Лексика та Граматика)", callback_data="quiz_cat_use_of_english")
    builder.button(text="🎯 Персональний симулятор помилок (190+)", callback_data="quiz_cat_personalized")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    
    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Розширена клавіатура адмін-панелі."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Додати питання НМТ", callback_data="admin_add_task")
    builder.button(text="📊 Точна статистика", callback_data="admin_stats")
    builder.button(text="🔍 Перевірити активних (Audit)", callback_data="admin_check_active")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    
    builder.adjust(1)
    return builder.as_markup()
