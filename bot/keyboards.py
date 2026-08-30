from typing import Optional
from urllib.parse import quote

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import (
    CATEGORY_READING,
    CATEGORY_USE_OF_ENGLISH,
    CATEGORY_PERSONALIZED,
    WEB_APP_URL,
)


def get_main_keyboard(
    web_app_url: Optional[str] = None,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚀 Розпочати тест НМТ",
        callback_data="start_quiz_menu",
    )

    builder.button(
        text="👤 Мій профіль",
        callback_data="show_profile",
    )

    builder.button(
        text="🎁 Запросити друга",
        callback_data="show_referral",
    )

    builder.button(
        text="⭐ Premium",
        callback_data="show_tariffs",
    )

    if web_app_url:
        builder.button(
            text="🌐 Навчальна платформа",
            web_app=WebAppInfo(url=web_app_url),
        )

    if is_admin:
        builder.button(
            text="⚡ Адмін-панель",
            callback_data="admin_panel",
        )

    builder.adjust(1)

    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚀 До тестів НМТ",
        callback_data="start_quiz_menu",
    )

    builder.button(
        text="🎁 Запросити друга",
        callback_data="show_referral",
    )

    builder.button(
        text="⭐ Premium",
        callback_data="show_tariffs",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def get_referral_keyboard(
    share_url: str,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="📤 Поділитися запрошенням",
            url=share_url,
        )
    )

    builder.button(
        text="👤 Мій профіль",
        callback_data="show_profile",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def get_tariffs_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="⭐ 3 дні Premium — 49 Stars",
        callback_data="buy_premium_3days",
    )

    builder.button(
        text="🌟 30 днів Premium — 199 Stars",
        callback_data="buy_premium_30days",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def get_quiz_categories_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📖 Reading",
        callback_data="quiz_cat_reading",
    )

    builder.button(
        text="🔤 Use of English",
        callback_data="quiz_cat_use_of_english",
    )

    builder.button(
        text="🎯 Симулятор помилок 190+",
        callback_data="quiz_cat_personalized",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def get_question_keyboard(
    question_id: str,
    options: dict,
    prefix: str = "quiz_answer",
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for letter in ("A", "B", "C", "D"):
        text = options.get(letter, letter)

        callback_data = (
            f"{prefix}:{question_id}:{letter}"
        )

        builder.button(
            text=f"{letter}. {text}",
            callback_data=callback_data,
        )

    builder.adjust(1)

    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text="➕ Додати питання НМТ",
        callback_data="admin_add_task",
    )

    builder.button(
        text="📊 Статистика",
        callback_data="admin_stats",
    )

    builder.button(
        text="🔍 Аудит активних",
        callback_data="admin_check_active",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def build_referral_share_url(
    bot_username: str,
    user_id: int,
) -> tuple[str, str]:

    ref_link = (
        f"https://t.me/{bot_username}"
        f"?start=ref_{user_id}"
    )

    share_text = (
        "🚀 Готуєшся до НМТ з англійської?\n\n"
        "Я знайшов тренажер, де можна швидко "
        "перевірити себе, побачити слабкі місця "
        "та тренувати саме формат НМТ.\n\n"
        "Спробуй експрес-тест 👇"
    )

    share_url = (
        "https://t.me/share/url"
        f"?url={quote(ref_link)}"
        f"&text={quote(share_text)}"
    )

    return ref_link, share_url
