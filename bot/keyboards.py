from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Тренировка", callback_data="start_practice")
    builder.button(text="🏆 Лиги и Рейтинг", callback_data="show_leaderboard")
    builder.adjust(1)
    return builder.as_markup()

def question_options_kb(question_id: str, options: list):
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.button(text=option, callback_data=f"ans_{question_id}_{idx}")
    builder.adjust(1)
    return builder.as_markup()

def next_question_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Следующий вопрос ➡️", callback_data="start_practice")
    builder.button(text="🏠 Меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()

def roadmap_kb(roadmap: list):
    builder = InlineKeyboardBuilder()

    for item in roadmap:
        if item["is_completed"]:
            status = "✅"
            cb = f"select_topic_{item['id']}"
        elif item["is_unlocked"]:
            status = "🎯 Current"
            cb = f"select_topic_{item['id']}"
        else:
            status = "🔒"
            cb = f"locked_{item['id']}"

        btn_text = f"{status} {item['icon']} {item['title']}"
        builder.button(text=btn_text, callback_data=cb)

    builder.adjust(1)
    return builder.as_markup()

def topic_action_kb(topic_id: str, is_unlocked: bool):
    builder = InlineKeyboardBuilder()
    if is_unlocked:
        builder.button(text="📖 Вчити тему", callback_data=f"start_learn_{topic_id}")
    builder.button(text="⚡ Скласти тест достроково (Skip)", callback_data=f"start_skip_test_{topic_id}")
    builder.button(text="🔙 Назад до карти", callback_data="show_roadmap")
    builder.adjust(1)
    return builder.as_markup()
