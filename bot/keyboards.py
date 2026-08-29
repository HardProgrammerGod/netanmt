import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.db_client import DBClient
from bot.keyboards import (
    get_main_keyboard, 
    get_difficulty_keyboard, 
    get_quiz_options_keyboard,
    get_explanation_keyboard
)

logger = logging.getLogger(__name__)
router = Router(name="main_router")

class QuizFSM(StatesGroup):
    in_quiz = State()

# ================= COMMAND /START =================
@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    # Витягуємо ID реферера з аргументів /start ref_123456
    referrer_id = None
    if command.args and command.args.startswith("ref_"):
        try:
            referrer_id = int(command.args.replace("ref_", ""))
        except ValueError:
            pass

    user = DBClient.get_or_create_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referrer_id=referrer_id
    )

    welcome_text = (
        f"Привіт, <b>{message.from_user.first_name}</b>! 👋\n\n"
        f"Вітаю в тренажері підготовки до **НМТ з англійської**! ⚡️\n\n"
        f"🔥 Твій поточний стрік: <b>{user.get('streak', 1)} днів</b>\n"
        f"🏆 Твої бали (XP): <b>{user.get('xp', 0)}</b>\n\n"
        f"Обирай розділ у меню нижче та прокачуй свій бал до 190+!"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# ================= MENU HANDLERS =================
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user = DBClient.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    
    welcome_text = (
        f"Головне меню 🎯\n\n"
        f"🔥 Стрік: <b>{user.get('streak', 1)} днів</b> | 🏆 XP: <b>{user.get('xp', 0)}</b>"
    )
    await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "start_quiz_menu")
async def show_difficulty_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Обери рівень складності тренування:\n\n"
        "🟢 <b>Рівень 1</b>: Легкий розігрів (A1-A2) — для швидкої впевненості\n"
        "🟡 <b>Рівень 2</b>: Пастки НМТ (B1) — типові помилки випускників\n"
        "🔴 <b>Рівень 3</b>: Хардкор (B2) — складні граматичні конструкції",
        reply_markup=get_difficulty_keyboard(),
        parse_mode="HTML"
    )

# ================= QUIZ LOGIC =================
@router.callback_query(F.data.startswith("quiz_diff_"))
async def start_quiz_by_diff(callback: types.CallbackQuery, state: FSMContext):
    difficulty = int(callback.data.split("_")[-1])
    questions = DBClient.get_questions_by_difficulty(difficulty=difficulty, limit=10)
    
    if not questions:
        await callback.answer("⚠️ Наразі питань цього рівня немає в базі. Спробуй інший!", show_alert=True)
        return

    await state.set_state(QuizFSM.in_quiz)
    await state.update_data(questions=questions, current_index=0, difficulty=difficulty)
    
    await send_next_question(callback.message, state)

async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions", [])
    index = data.get("current_index", 0)

    if index >= len(questions):
        await state.clear()
        user = DBClient.get_or_create_user(message.chat.id, message.chat.from_user.username, message.chat.from_user.first_name)
        await message.answer(
            f"🎉 <b>Вітаємо! Сесію завершено!</b>\n\n"
            f"Ти пройшов блок питань. Твій загальний результат: <b>{user.get('xp', 0)} XP</b>.\n"
            f"Не зупиняйся, підтримуй свій щоденний стрік! 🔥",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return

    q = questions[index]
    text = f"<b>Питання {index + 1}/{len(questions)}:</b>\n\n{q['question_text']}"
    
    kb = get_quiz_options_keyboard(question_id=q["id"], options=q["options"])
    
    if message.text:
        await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(QuizFSM.in_quiz, F.data.startswith("answer_"))
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    _, q_id_str, opt_idx_str = callback.data.split("_")
    q_id = int(q_id_str)
    selected_option = int(opt_idx_str)

    q = DBClient.get_question_by_id(q_id)
    if not q:
        await callback.answer("Помилка отримання питання.", show_alert=True)
        return

    user = DBClient.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    is_correct = (selected_option == q["correct_option"])
    is_premium = user.get("is_premium", False)

    data = await state.get_data()
    await state.update_data(current_index=data.get("current_index", 0) + 1)

    if is_correct:
        DBClient.add_xp(callback.from_user.id, amount=10)
        res_text = "✅ <b>Правильно! +10 XP</b> 🎉\n\n"
        if q.get("explanation"):
            res_text += f"💡 <i>{q['explanation']}</i>"
    else:
        res_text = f"❌ <b>Неправильно!</b>\nПравильна відповідь: <b>{q['options'][q['correct_option']]}</b>\n\n"
        if is_premium and q.get("explanation"):
            res_text += f"💡 <b>Пояснення від викладача:</b>\n{q['explanation']}"
        else:
            res_text += "🔒 <i>Повне розширене пояснення та відео-розбір доступні у Premium / Школі!</i>"

    await callback.message.edit_text(
        res_text,
        reply_markup=get_explanation_keyboard(is_premium=is_premium),
        parse_mode="HTML"
    )

@router.callback_query(QuizFSM.in_quiz, F.data == "next_question")
async def next_question_callback(callback: types.CallbackQuery, state: FSMContext):
    await send_next_question(callback.message, state)

# ================= REFERRAL & TARIFFS =================
@router.callback_query(F.data == "show_referral")
async def show_referral(callback: types.CallbackQuery):
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{callback.from_user.id}"
    
    user = DBClient.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    ref_count = user.get("referrals_count", 0)

    text = (
        f"🎁 <b>Запрошуй друзів — отримуй Premium безкоштовно!</b>\n\n"
        f"Твоє реферальне посилання:\n<code>{ref_link}</code>\n\n"
        f"👥 Запрошено друзів: <b>{ref_count}</b>\n"
        f"💡 <i>За кожні 2 запрошених друзів ти отримуєш безкоштовний доступ до Premium-пояснень!</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "show_tariffs")
async def show_tariffs(callback: types.CallbackQuery):
    text = (
        "👑 <b>Тарифи підготовки до НМТ з англійської:</b>\n\n"
        "1️⃣ <b>PREMIUM (199 грн/міс)</b>\n"
        "• Пояснення та розбори до ВСІХ складних питань\n"
        "• Симулятори НМТ на час\n"
        "• Доступ до інтерактивних автовебінарів\n\n"
        "2️⃣ <b>ШКОЛА FULL (990 грн/міс)</b>\n"
        "• Все, що входить у Premium\n"
        "• Закритий чат із викладачем/ментором\n"
        "• 2 живих вебінари на тиждень + перевірка домашніх\n\n"
        "Для покупки або консультації тисни кнопку нижче або пиши адміну!"
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
