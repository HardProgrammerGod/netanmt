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
