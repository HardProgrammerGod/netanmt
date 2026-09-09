from typing import Optional
from urllib.parse import quote

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import (
    CHANNEL_URL,
    MANAGER_DISCOUNT_PERCENT,
)


def get_main_keyboard(
    daily_completed: bool = False,
    web_app_url: Optional[str] = None,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:
    """Minimal home screen: one primary habit action, two product actions, one more menu."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=("✅ Daily виконано" if daily_completed else "⚡ Сьогодні · 3 хв"),
            callback_data=("daily_done_info" if daily_completed else "start_daily"),
        )
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Тренування", callback_data="start_quiz_menu"),
        InlineKeyboardButton(text="📊 Прогрес", callback_data="show_progress"),
    )
    builder.row(InlineKeyboardButton(text="••• Ще", callback_data="show_more"))

    if is_admin:
        builder.row(InlineKeyboardButton(text="⚡ Адмін-панель", callback_data="admin_panel"))

    return builder.as_markup()


def get_more_keyboard(
    web_app_url: Optional[str] = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Premium", callback_data="show_tariffs")
    builder.button(text="👥 Готуватися з другом", callback_data="show_referral")
    builder.button(text="👤 Профіль", callback_data="show_profile")

    if CHANNEL_URL:
        builder.row(
            InlineKeyboardButton(
                text="📣 Канал Neta · короткі розбори",
                url=CHANNEL_URL,
            )
        )

    if web_app_url:
        builder.row(
            InlineKeyboardButton(
                text="🌐 Навчальна платформа",
                web_app=WebAppInfo(url=web_app_url),
            )
        )

    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Daily", callback_data="start_daily")
    builder.button(text="📊 Детальний прогрес", callback_data="show_progress")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_progress_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Daily · 3 хв", callback_data="start_daily")
    builder.button(text="🎯 Слабкі теми", callback_data="quiz_cat_personalized")
    builder.button(text="🧪 NMT Practice 32", callback_data="quiz_full_simulation")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_referral_keyboard(share_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📤 Запросити друга в Telegram",
            url=share_url,
        )
    )
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_daily_result_keyboard(
    show_referral: bool = False,
    share_url: Optional[str] = None,
    show_channel: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Ще 5 персональних", callback_data="quiz_cat_personalized")
    builder.button(text="📊 Мій прогрес", callback_data="show_progress")

    if show_referral and share_url:
        builder.row(
            InlineKeyboardButton(
                text="👥 Запросити друга тримати серію",
                url=share_url,
            )
        )

    if show_channel and CHANNEL_URL:
        builder.row(
            InlineKeyboardButton(
                text="📣 2-хв розбори в каналі Neta",
                url=CHANNEL_URL,
            )
        )

    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_daily_done_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Продовжити ще 5", callback_data="quiz_cat_personalized")
    builder.button(text="📊 Подивитися прогрес", callback_data="show_progress")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()



def get_daily_reminder_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Зробити Daily · 3 хв", callback_data="start_daily")
    return builder.as_markup()

def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ 3 дні Premium — 49 Stars", callback_data="buy_premium_3days")
    builder.button(text="🌟 30 днів Premium — 199 Stars", callback_data="buy_premium_30days")
    builder.button(
        text=f"💳 3 дні через менеджера — -{MANAGER_DISCOUNT_PERCENT}%",
        callback_data="manager_premium_3days",
    )
    builder.button(
        text=f"💳 30 днів через менеджера — -{MANAGER_DISCOUNT_PERCENT}%",
        callback_data="manager_premium_30days",
    )
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_manager_payment_keyboard(manager_username: str, draft_text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    manager_url = (
        f"https://t.me/{manager_username.lstrip('@')}"
        f"?text={quote(draft_text)}"
    )
    builder.row(InlineKeyboardButton(text="💬 Написати менеджеру", url=manager_url))
    builder.button(text="⭐ Інші способи оплати", callback_data="show_tariffs")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_quiz_categories_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📖 Reading", callback_data="quiz_cat_reading"),
        InlineKeyboardButton(text="🔤 Use of English", callback_data="quiz_cat_use_of_english"),
    )
    builder.row(InlineKeyboardButton(text="🎯 Мої слабкі теми", callback_data="quiz_cat_personalized"))
    builder.row(InlineKeyboardButton(text="🔥 Premium Focus · 10", callback_data="quiz_premium_focus"))
    builder.row(InlineKeyboardButton(text="🧪 NMT Practice 32", callback_data="quiz_full_simulation"))
    builder.row(InlineKeyboardButton(text="⬅️ Головне меню", callback_data="back_to_main"))
    return builder.as_markup()


def get_question_keyboard(
    question_id: str,
    options: dict,
    prefix: str = "quiz_answer",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for letter in ("A", "B", "C", "D"):
        text = options.get(letter, letter)
        callback_data = f"{prefix}:{question_id}:{letter}"
        builder.button(text=f"{letter}. {text}", callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()


def get_diagnostic_result_keyboard(
    share_url: Optional[str] = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Почати мій Daily", callback_data="start_daily")
    builder.button(text="🎯 Прокачати слабкі теми", callback_data="start_personalized_after_diagnostic")
    if share_url:
        builder.row(
            InlineKeyboardButton(
                text="👥 Порівняти результат з другом",
                url=share_url,
            )
        )
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Додати питання НМТ", callback_data="admin_add_task")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="📈 Воронка + retention", callback_data="admin_growth_funnel")
    builder.button(text="🔍 Аудит активних", callback_data="admin_check_active")
    builder.button(text="🚀 Launch / waitlist", callback_data="admin_launch_waitlist")
    builder.button(text="⬅️ Головне меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def build_referral_share_url(bot_username: str, user_id: int) -> tuple[str, str]:
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    share_text = (
        "⚡ Я готуюсь до НМТ з англійської в Neta по 3 хвилини на день.\n\n"
        "Там спочатку 12 коротких питань, а потім бот сам підбирає слабкі теми й повторює помилки. "
        "Зайди за моїм посиланням — порівняємо старт і потримаємо серію разом 👇"
    )
    share_url = (
        "https://t.me/share/url"
        f"?url={quote(ref_link)}"
        f"&text={quote(share_text)}"
    )
    return ref_link, share_url
