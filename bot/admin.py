from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import ADMIN_IDS
from bot.db_client import DBClient

admin_router = Router()

class AddTaskFSM(StatesGroup):
    category = State()
    sub_category = State()
    question_text = State()
    options = State()
    correct_answer = State()
    explanation = State()

@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати питання НМТ", callback_query_data="admin_add_task")],
        [InlineKeyboardButton(text="📊 Статистика", callback_query_data="admin_stats")]
    ])
    await message.answer("🛠 <b>Адмін-панель НМТ Англійська</b>", parse_mode="HTML", reply_markup=kb)

@admin_router.callback_query(F.data == "admin_add_task")
async def start_add_task(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AddTaskFSM.category)
    await call.message.answer("Введіть категорію НМТ (наприклад: Reading, Use of English, Grammar):")

@admin_router.message(AddTaskFSM.category)
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddTaskFSM.sub_category)
    await message.answer("Введіть підкатегорію (наприклад: Tenses, Vocabulary, Matching):")

@admin_router.message(AddTaskFSM.sub_category)
async def process_sub_category(message: Message, state: FSMContext):
    await state.update_data(sub_category=message.text)
    await state.set_state(AddTaskFSM.question_text)
    await message.answer("Введіть текст питання / завдання:")

@admin_router.message(AddTaskFSM.question_text)
async def process_question(message: Message, state: FSMContext):
    await state.update_data(question_text=message.text)
    await state.set_state(AddTaskFSM.options)
    await message.answer("Введіть 4 варіанти відповідей через кому (наприклад: A) go, B) went, C) gone, D) going):")

@admin_router.message(AddTaskFSM.options)
async def process_options(message: Message, state: FSMContext):
    opts = [opt.strip() for opt.strip().split(",")]
    options_dict = {"A": opts[0], "B": opts[1] if len(opts)>1 else "", "C": opts[2] if len(opts)>2 else "", "D": opts[3] if len(opts)>3 else ""}
    await state.update_data(options=options_dict)
    await state.set_state(AddTaskFSM.correct_answer)
    await message.answer("Вкажіть правильну відповідь (наприклад: A, B, C або D):")

@admin_router.message(AddTaskFSM.correct_answer)
async def process_correct(message: Message, state: FSMContext):
    await state.update_data(correct_answer=message.text.strip().upper())
    await state.set_state(AddTaskFSM.explanation)
    await message.answer("Введіть пояснення до правила/відповіді (або '-' якщо відсутнє):")

@admin_router.message(AddTaskFSM.explanation)
async def process_explanation(message: Message, state: FSMContext):
    data = await state.get_data()
    explanation = message.text if message.text != "-" else ""
    
    await DBClient.add_task(
        category=data["category"],
        sub_category=data["sub_category"],
        section="NMT",
        question_text=data["question_text"],
        options=data["options"],
        correct_answer=data["correct_answer"],
        explanation=explanation
    )
    await state.clear()
    await message.answer("✅ <b>Питання НМТ успішно додано до бази!</b>", parse_mode="HTML")
