from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard(web_app_url: str = None, is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🚀 Розпочати тест", callback_data="start_quiz_menu")
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
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 До тестів", callback_data="start_quiz_menu")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Купити Premium (1 місяць)", callback_data="buy_premium_1m")
    builder.button(text="🎓 Навчання в Neta School", callback_data="buy_neta_school")
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

def get_quiz_options_keyboard(question_id: int, options: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, option_text in enumerate(options):
        builder.button(
            text=str(option_text),
            callback_data=f"answer_{question_id}_{idx}"
        )
    builder.adjust(1)
    return builder.as_markup()

def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика бота", callback_data="admin_stats")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()
