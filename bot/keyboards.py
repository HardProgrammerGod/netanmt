from typing import Optional
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# ----------------------------------------------------------------------
# Callback Data Factories (Типізована обробка callback-запитів)
# ----------------------------------------------------------------------
class MenuCallback(CallbackData, prefix="menu"):
    action: str
    item_id: Optional[int] = None


class NavigationCallback(CallbackData, prefix="nav"):
    page: int


# ----------------------------------------------------------------------
# Inline Keyboards
# ----------------------------------------------------------------------
def get_main_inline_keyboard() -> InlineKeyboardMarkup:
    """Головна inline-клавіатура користувача."""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="👤 Профіль", 
        callback_data=MenuCallback(action="profile")
    )
    builder.button(
        text="⚙️ Налаштування", 
        callback_data=MenuCallback(action="settings")
    )
    builder.button(
        text="ℹ️ Допомога", 
        callback_data=MenuCallback(action="help")
    )
    
    # Регулювання ґратки: 2 кнопки в першому рядку, 1 у другому
    builder.adjust(2, 1)
    return builder.as_markup()


def get_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Універсальна клавіатура для пагінації (гортання)."""
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.button(
            text="⬅️ Назад", 
            callback_data=NavigationCallback(page=current_page - 1)
        )
    
    builder.button(
        text=f"📄 {current_page}/{total_pages}", 
        callback_data="ignore"
    )
    
    if current_page < total_pages:
        builder.button(
            text="Вперед ➡️", 
            callback_data=NavigationCallback(page=current_page + 1)
        )
        
    builder.adjust(3)
    return builder.as_markup()


# ----------------------------------------------------------------------
# Reply Keyboards (Текстові кнопки під полем вводу)
# ----------------------------------------------------------------------
def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Головне меню текстових кнопок."""
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="🚀 Головне меню")
    builder.button(text="📊 Статистика")
    builder.button(text="📞 Підтримка")
    
    builder.adjust(2, 1)
    return builder.as_markup(
        resize_keyboard=True,
        persistent=True
    )
