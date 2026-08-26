import logging
from aiogram import Router, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Імпортуємо клавіатури та фабрики callback-даних
from bot.keyboards import (
    get_main_inline_keyboard,
    get_main_reply_keyboard,
    MenuCallback,
    NavigationCallback
)

logger = logging.getLogger(__name__)

# Створюємо роутер для підключення у main.py / Dispatcher
router = Router(name="main_router")


# ----------------------------------------------------------------------
# FSM (Машина станів)
# ----------------------------------------------------------------------
class FormState(StatesGroup):
    waiting_for_name = State()
    waiting_for_confirmation = State()


# ----------------------------------------------------------------------
# Command Handlers
# ----------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обробка команди /start."""
    await state.clear()  # Скидаємо попередній стан для безпеки
    
    user_name = html.bold(message.from_user.full_name)
    welcome_text = (
        f"Вітаю, {user_name}!\n\n"
        "Бот працює швидко та безпечно. Оберіть потрібну дію з меню нижче:"
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_reply_keyboard()
    )
    await message.answer(
        text="Швидке керування:",
        reply_markup=get_main_inline_keyboard()
    )


@router.message(Command("help"))
@router.message(F.text == "📞 Підтримка")
async def cmd_help(message: Message) -> None:
    """Обробка команди /help та відповідної кнопки."""
    await message.answer(
        text="ℹ️ **Центр допомоги**\n\nЯкщо у вас виникли питання, зверніться до адміністратора."
    )


# ----------------------------------------------------------------------
# Inline Callback Handlers
# ----------------------------------------------------------------------
@router.callback_query(MenuCallback.filter(F.action == "profile"))
async def process_profile_callback(
    query: CallbackQuery, 
    callback_data: MenuCallback,
    # db_session: AsyncSession  <-- якщо передаєте сесію БД через Middleware
) -> None:
    """Відображення профілю користувача."""
    await query.answer()  # Обов'язково закриваємо спінер на кнопці
    
    user_id = query.from_user.id
    username = query.from_user.username or "Не вказано"
    
    profile_text = (
        f"👤 **Ваш профіль**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"🏷 Username: @{username}\n"
    )
    
    # Редагуємо повідомлення безпечно
    if query.message:
        await query.message.edit_text(
            text=profile_text,
            reply_markup=get_main_inline_keyboard()
        )


@router.callback_query(MenuCallback.filter(F.action == "settings"))
async def process_settings_callback(query: CallbackQuery) -> None:
    """Розділ налаштувань."""
    await query.answer("Налаштування у розробці", show_alert=True)


@router.callback_query(F.data == "ignore")
async def process_ignore_callback(query: CallbackQuery) -> None:
    """Заглушка для інформаційних кнопок."""
    await query.answer()


# ----------------------------------------------------------------------
# Text & FSM Handlers
# ----------------------------------------------------------------------
@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message) -> None:
    """Приклад обробки кнопки статистики."""
    await message.answer("📊 Система працює в штатному режимі. Uptime: 99.9%.")


@router.message(F.text == "🚀 Головне меню")
async def return_to_main(message: Message, state: FSMContext) -> None:
    """Повернення до головного меню."""
    await state.clear()
    await message.answer(
        text="Ви повернулися в головне меню.",
        reply_markup=get_main_inline_keyboard()
    )
