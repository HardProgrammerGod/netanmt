from urllib.parse import quote

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import (
    ADMIN_USERNAME,
    STARS_3_DAYS,
    STARS_30_DAYS,
)


def get_main_keyboard(
    web_app_url: str = "",
    is_admin: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚀 Розпочати тест НМТ",
        callback_data="start_quiz_menu",
    )

    builder.button(
        text="🔥 Мій Streak & Профіль",
        callback_data="show_profile",
    )

    builder.button(
        text="🎁 Запросити друга",
        callback_data="show_referral",
    )

    builder.button(
        text="👑 Premium",
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
        text="👑 Premium",
        callback_data="show_tariffs",
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
        text=f"⭐ {STARS_3_DAYS} — Premium на 3 дні",
        callback_data="buy_premium_3days",
    )

    builder.button(
        text=f"⭐ {STARS_30_DAYS} — Premium на 30 днів",
        callback_data="buy_premium_30days",
    )

    builder.button(
        text="💬 Написати менеджеру",
        url=(
            f"https://t.me/{ADMIN_USERNAME}"
            f"?text={quote('Привіт! Хочу дізнатися про Premium для НМТ.')}"
        ),
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
        text="📝 Reading",
        callback_data="quiz_cat_reading",
    )

    builder.button(
        text="🔤 Use of English",
        callback_data="quiz_cat_use_of_english",
    )

    builder.button(
        text="🎯 Персональний симулятор помилок (190+)",
        callback_data="quiz_cat_personalized",
    )

    builder.button(
        text="⬅️ Головне меню",
        callback_data="back_to_main",
    )

    builder.adjust(1)

    return builder.as_markup()


def get_answer_keyboard(
    task_id: int,
    options: dict[str, str],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for letter in ("A", "B", "C", "D"):
        builder.button(
            text=f"{letter}. {options.get(letter, '')}",
            callback_data=f"quiz_answer:{task_id}:{letter}",
        )

    builder.adjust(1)

    return builder.as_markup()


def get_retention_answer_keyboard(
    task_id: int,
    options: dict[str, str],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for letter in ("A", "B", "C", "D"):
        builder.button(
            text=f"{letter}. {options.get(letter, '')}",
            callback_data=f"retention_answer:{task_id}:{letter}",
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


def get_admin_category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Reading",
                    callback_data="admin_category:Reading",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔤 Use of English",
                    callback_data="admin_category:Use of English",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 190+",
                    callback_data=(
                        "admin_category:"
                        "Персональний симулятор помилок (190+)"
                    ),
                )
            ],
        ]
    )


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data="admin_cancel",
                )
            ]
        ]
    )
