from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppProperty
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard(web_app_url: str = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🚀 Розпочати тест (Duolingo Style)", callback_data="start_quiz_menu")
    builder.button(text="🔥 Мій Стрік & Профіль", callback_data="show_profile")
    builder.button(text="🎁 Запросити друга (+Premium)", callback_data="show_referral")
    builder.button(text="👑 Premium / Школа NMT", callback_data="show_tariffs")
    
    if web_app_url:
        builder.button(text="🌐 Навчальна Платформа (WebApp)", web_app=WebAppProperty(url=web_app_url))

    builder.adjust(1)
    return builder.as_markup()

def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Рівень 1: Розігрів (A1-A2)", callback_data="quiz_diff_1")
    builder.button(text="🟡 Рівень 2: Пастки НМТ (B1)", callback_data="quiz_diff_2")
    builder.button(text="🔴 Рівень 3: Хардкор 190+ (B2)", callback_data="quiz_diff_3")
    builder.button(text="⬅️ Назад", callback_data="back_to_main")
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

def get_explanation_keyboard(is_premium: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Наступне питання", callback_data="next_question")
    if not is_premium:
        builder.button(text="🔒 Отримати розбір від викладача (Premium)", callback_data="show_tariffs")
    builder.adjust(1)
    return builder.as_markup()
