import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🗺 Карта навчання")
    builder.button(text="👤 Профіль")
    builder.button(text="🏆 Лідерборд")
    builder.button(text="⭐ Купити Premium")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True, persistent=True)

def get_premium_payment_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопка інвойсу для Зірок (250 Stars)
    builder.button(
        text="⭐ Оплатити 250 Stars (270 грн)", 
        callback_data="buy_premium_stars"
    )
    
    # 2. Формуємо посилання tg://msg_url з готовим текстом
    msg_text = "Привіт, хочу купити преміум в боті картою!"
    encoded_text = urllib.parse.quote(msg_text)
    manager_url = f"https://t.me/nnopkam?text={encoded_text}"
    
    builder.button(
        text="💳 Картка (знижка -27% — 200 грн)", 
        url=manager_url
    )
    
    builder.adjust(1)
    return builder.as_markup()

def roadmap_kb(roadmap: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not roadmap:
        builder.button(text="🔄 Оновити", callback_data="show_roadmap")
        return builder.as_markup()

    for item in roadmap:
        if item["is_completed"]:
            status = "✅"
        elif item["is_unlocked"]:
            status = "🎯 В процесі"
        else:
            status = "🔒"

        btn_text = f"{status} {item['icon']} {item['title']}"
        builder.button(text=btn_text, callback_data=f"select_topic_{item['id']}")

    builder.adjust(1)
    return builder.as_markup()

def topic_action_kb(topic_id: str, is_unlocked: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_unlocked:
        builder.button(text="📖 Вчити тему (Тест)", callback_data=f"start_learn_{topic_id}")
        builder.button(text="⚡ Тест-пропуск (Skip)", callback_data=f"start_skip_{topic_id}")
    else:
        builder.button(text="🔒 Тест для розблокування", callback_data=f"start_skip_{topic_id}")
    
    builder.button(text="🔙 Назад до карти", callback_data="show_roadmap")
    builder.adjust(1)
    return builder.as_markup()

def test_answers_kb(options: list, question_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.button(text=f"{idx + 1}. {option}", callback_data=f"ans_{idx}")
    builder.adjust(1)
    return builder.as_markup()
