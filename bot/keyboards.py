from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Спробувати Neta Memory · 3 питання", callback_data="start_intro")
    return b.as_markup()


def get_main_keyboard(daily_completed: bool = False, is_admin: bool = False, **_) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(
        text="✓ Сьогодні виконано" if daily_completed else "⚡ Заняття на сьогодні · ~4 хв",
        callback_data="start_today",
    ))
    b.row(
        InlineKeyboardButton(text="Мій прогрес", callback_data="show_progress"),
        InlineKeyboardButton(text="З друзями", callback_data="show_friends"),
    )
    b.row(
        InlineKeyboardButton(text="Про курс", callback_data="show_course"),
        InlineKeyboardButton(text="Налаштування", callback_data="show_settings"),
    )
    b.row(InlineKeyboardButton(text="Канал · розбори НМТ", callback_data="show_channel"))
    if is_admin:
        b.row(InlineKeyboardButton(text="Адмін-панель", callback_data="admin_panel"))
    return b.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    ]])


def get_question_keyboard(session_id: str, question_index: int, options: dict | None = None) -> InlineKeyboardMarkup:
    # Full option text is rendered in the message. Compact buttons prevent
    # Telegram from truncating long NMT answers on mobile.
    b = InlineKeyboardBuilder()
    for row in (("A", 0, "B", 1), ("C", 2, "D", 3)):
        b.row(
            InlineKeyboardButton(text=row[0], callback_data=f"learn_answer:{session_id}:{question_index}:{row[1]}"),
            InlineKeyboardButton(text=row[2], callback_data=f"learn_answer:{session_id}:{question_index}:{row[3]}"),
        )
    return b.as_markup()


def get_intro_result_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⚡ Перше заняття · ~4 хв", callback_data="start_today"))
    b.row(InlineKeyboardButton(text="Канал · безкоштовні розбори", callback_data="show_channel"))
    return b.as_markup()


def get_daily_result_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Подивитися прогрес", callback_data="show_progress"))
    b.row(InlineKeyboardButton(text="Канал · розбори НМТ", callback_data="show_channel"))
    return b.as_markup()


def get_diagnostic_result_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Повернутися до прогресу", callback_data="show_progress"))
    b.row(InlineKeyboardButton(text="Заняття на сьогодні", callback_data="start_today"))
    return b.as_markup()


def get_progress_keyboard(has_new_diagnostic: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if not has_new_diagnostic:
        b.row(InlineKeyboardButton(text="Карта навичок · 12 питань", callback_data="start_diagnostic"))
    b.row(InlineKeyboardButton(text="⚡ Заняття на сьогодні", callback_data="start_today"))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    return b.as_markup()


def get_reminder_offer_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="17:00", callback_data="reminder_set:17:00"),
        InlineKeyboardButton(text="19:00", callback_data="reminder_set:19:00"),
        InlineKeyboardButton(text="21:00", callback_data="reminder_set:21:00"),
    )
    b.row(InlineKeyboardButton(text="Не зараз", callback_data="reminder_skip"))
    return b.as_markup()


def get_settings_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if enabled:
        b.button(text="Вимкнути нагадування", callback_data="reminder_off")
    else:
        b.row(
            InlineKeyboardButton(text="17:00", callback_data="reminder_set:17:00"),
            InlineKeyboardButton(text="19:00", callback_data="reminder_set:19:00"),
            InlineKeyboardButton(text="21:00", callback_data="reminder_set:21:00"),
        )
    b.row(InlineKeyboardButton(text="Приватність", callback_data="show_privacy"))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    return b.as_markup()


def get_privacy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Назад до налаштувань", callback_data="show_settings")
    ]])


def get_course_keyboard(interested: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if not interested:
        b.button(text="Мені цікаво", callback_data="course_interest")
    b.button(text="Назад", callback_data="back_to_main")
    b.adjust(1)
    return b.as_markup()


def get_channel_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Відкрити @neta_nmt", url=channel_url))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    return b.as_markup()


def get_friends_keyboard(share_url: str, leaderboard_opt_in: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Запросити друга", url=share_url))
    b.row(InlineKeyboardButton(
        text=("Вийти з рейтингу" if leaderboard_opt_in else "Увійти в рейтинг"),
        callback_data=("leaderboard_off" if leaderboard_opt_in else "leaderboard_on"),
    ))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    return b.as_markup()


def build_referral_share_url(bot_username: str, user_id: int) -> tuple[str, str]:
    ref_link = f"https://t.me/{bot_username}?start=ref_{int(user_id)}"
    text = "Готуюсь до НМТ з англійської в Neta: короткі заняття, повторення помилок і прогрес. Якщо хочеш — приєднуйся:"
    share_url = f"https://t.me/share/url?url={quote(ref_link)}&text={quote(text)}"
    return ref_link, share_url


# Kept for the existing admin router.
def get_admin_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Додати питання НМТ", callback_data="admin_add_task")
    b.button(text="📊 Статистика", callback_data="admin_stats")
    b.button(text="📈 Воронка + retention", callback_data="admin_growth_funnel")
    b.button(text="🧭 Learning report", callback_data="admin_learning_report")
    b.button(text="🔍 Аудит активних", callback_data="admin_check_active")
    b.button(text="🚀 Launch / waitlist", callback_data="admin_launch_waitlist")
    b.button(text="⬅️ Головне меню", callback_data="back_to_main")
    b.adjust(1)
    return b.as_markup()
