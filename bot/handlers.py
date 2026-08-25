from aiogram import Router, types, F
from aiogram.filters import CommandStart
from bot.db_client import DBClient
from bot.keyboards import main_menu_kb, question_options_kb, next_question_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    args = message.text.split()
    ref_id = int(args[1].replace("ref_", "")) if len(args) > 1 and args[1].startswith("ref_") else None

    user, _ = DBClient.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referrer_id=ref_id
    )

    text = (
        f"Привет, {user['first_name']}! 🐾\n\n"
        f"📊 Уровень: {user['level']} | XP: {user['xp']}\n"
        f"⚡ Энергия: {user['energy']}/{user['max_energy']}\n\n"
        f"Готов прокачать английский к НМТ?"
    )
    await message.answer(text, reply_markup=main_menu_kb())

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await cmd_start(callback.message)
    await callback.answer()

@router.callback_query(F.data == "start_practice")
async def start_practice(callback: types.CallbackQuery):
    q = DBClient.get_next_question(callback.from_user.id)
    if not q:
        await callback.message.edit_text("В базе пока нет вопросов!", reply_markup=main_menu_kb())
        return

    text = f"<b>Тема:</b> {q['topic'].upper()}\n\n{q['question_text']}"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=question_options_kb(q['id'], q['options']))

@router.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: types.CallbackQuery):
    _, q_id, selected_idx = callback.data.split("_")
    selected_idx = int(selected_idx)
    
    res = DBClient.supabase.table("questions").select("*").eq("id", q_id).execute()
    if not res.data:
        await callback.answer("Ошибка доступа к вопросу.")
        return
        
    question = res.data[0]
    is_correct = (selected_idx == question["correct_option"])
    DBClient.record_answer(callback.from_user.id, q_id, is_correct)

    if is_correct:
        response_text = f"✅ <b>Правильно! (+15 XP)</b>\n\n<i>{question.get('explanation', '')}</i>"
    else:
        correct_text = question["options"][question["correct_option"]]
        response_text = f"❌ <b>Неверно!</b>\nПравильный ответ: {correct_text}\n\n<i>{question.get('explanation', '')}</i>"

    await callback.message.edit_text(response_text, parse_mode="HTML", reply_markup=next_question_kb())

@router.callback_query(F.data == "show_leaderboard")
async def show_leaderboard(callback: types.CallbackQuery):
    leaders = DBClient.get_leaderboard()
    text = "🏆 <b>ТОП-10 УЧЕНИКОВ НЕДЕЛИ:</b>\n\n"
    for item in leaders:
        name = item['first_name'] or item['username'] or "Аноним"
        text += f"{item['rank']}. {name} — {item['xp']} XP (Ур. {item['level']})\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=main_menu_kb())
