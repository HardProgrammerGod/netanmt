import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import (
    get_main_reply_keyboard, 
    get_premium_payment_kb,
    roadmap_kb, 
    topic_action_kb, 
    test_answers_kb
)
from bot.db_client import DBClient

logger = logging.getLogger(__name__)
router = Router(name="main_router")

# --- FSM Стан для тестування ---
class QuizStates(StatesGroup):
    in_quiz = State()

# --- Головне меню та Навігація ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    args = message.text.split()
    referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    user, is_new = DBClient.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        referrer_id=referrer_id
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це твій інтерактивний тренажер підготовки до НМТ з англійської мови.\n"
        "Обирай розділ у меню нижче та розпочинай підготовку!"
    )
    if is_new and referrer_id:
        welcome_text += "\n\n🎁 **Ви зареєструвалися за реферальним посиланням!**"

    await message.answer(welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown")

@router.message(F.text == "👤 Профіль")
async def show_profile(message: Message):
    user, _ = DBClient.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or ""
    )
    if not user:
        await message.answer("⚠️ Не вдалося завантажити дані профілю.")
        return

    status = "⭐ Premium (Безлімітна енергія)" if user.get("is_premium") else "👤 Звичайний"
    energy_val = "♾️" if user.get("is_premium") else f"{user.get('energy', 0)}/5"
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"

    profile_text = (
        f"📊 **Твій Особистий Профіль:**\n\n"
        f"👤 Ім'я: **{user.get('first_name', '')}**\n"
        f"Статус: **{status}**\n"
        f"⚡ Енергія: **{energy_val}**\n"
        f"🏆 Набрано XP: **{user.get('xp', 0)}**\n\n"
        f"🔗 **Твоє реферальне посилання:**\n`{ref_link}`\n"
        f"_(Отримуй +100 XP за кожного запрошеного друга!)_"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@router.message(F.text == "🗺 Карта навчання")
async def show_roadmap_cmd(message: Message):
    roadmap = DBClient.get_user_roadmap(message.from_user.id)
    if not roadmap:
        await message.answer("Розділи навчання зараз наповнюються. Завітайте трохи пізніше!")
        return
    await message.answer("🗺 **Твоя карта навчання НМТ:**", reply_markup=roadmap_kb(roadmap), parse_mode="Markdown")

@router.callback_query(F.data == "show_roadmap")
async def show_roadmap_cb(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.answer()
    roadmap = DBClient.get_user_roadmap(query.from_user.id)
    await query.message.edit_text("🗺 **Твоя карта навчання НМТ:**", reply_markup=roadmap_kb(roadmap), parse_mode="Markdown")

@router.callback_query(F.data.startswith("select_topic_"))
async def select_topic(query: CallbackQuery):
    await query.answer()
    topic_id = query.data.replace("select_topic_", "")
    roadmap = DBClient.get_user_roadmap(query.from_user.id)
    topic = next((t for t in roadmap if str(t["id"]) == str(topic_id)), None)
    
    if not topic:
        await query.message.answer("Розділ не знайдено.")
        return

    text = f"Розділ: **{topic['title']}**\n\nОбери необхідну дію:"
    await query.message.edit_text(text, parse_mode="Markdown", reply_markup=topic_action_kb(topic_id, topic["is_unlocked"]))

@router.message(F.text == "🏆 Лідерборд")
async def show_leaderboard(message: Message):
    leaders = DBClient.get_leaderboard()
    if not leaders:
        await message.answer("🏆 Лідерборд поки порожній. Будь першим!")
        return

    text = "🏆 **Топ-10 студентів тижня:**\n\n"
    for idx, l in enumerate(leaders, 1):
        name = l.get("first_name") or l.get("username") or "Студент"
        text += f"{idx}. **{name}** — {l.get('xp', 0)} XP\n"

    await message.answer(text, parse_mode="Markdown")

# --- Логіка Тестування (FSM Engine) ---

@router.callback_query(F.data.startswith(("start_learn_", "start_skip_")))
async def start_quiz(query: CallbackQuery, state: FSMContext):
    await query.answer()
    topic_id = query.data.split("_")[-1]
    questions = DBClient.get_test_questions(topic_id=topic_id, limit=5)

    if not questions:
        await query.message.edit_text(
            "⚠️ У цій темі ще немає питань. Адміністратор скоро їх додасть!",
            reply_markup=roadmap_kb(DBClient.get_user_roadmap(query.from_user.id))
        )
        return

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=questions,
        current_index=0,
        correct_count=0,
        topic_id=topic_id
    )

    await send_next_question(query.message, state)

async def send_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data["current_index"]
    questions = data["questions"]

    if q_index >= len(questions):
        correct = data["correct_count"]
        total = len(questions)
        topic_id = data["topic_id"]
        user_id = message.chat.id

        is_passed = (correct / total) >= 0.6

        if is_passed:
            DBClient.unlock_topic(user_id, topic_id)
            res_text = f"🎉 **Вітаємо! Тест складено!**\n\nРезультат: **{correct}/{total}**\nТему успішно зараховано!"
        else:
            res_text = f"❌ **Тест не складено.**\n\nРезультат: **{correct}/{total}**\nСпробуйте ще раз, щоб відкрити наступні теми."

        await state.clear()
        await message.edit_text(
            res_text, 
            parse_mode="Markdown", 
            reply_markup=roadmap_kb(DBClient.get_user_roadmap(user_id))
        )
        return

    q = questions[q_index]
    text = f"❓ **Питання {q_index + 1}/{len(questions)}:**\n\n{q['question_text']}"
    
    await message.edit_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=test_answers_kb(q['options'], str(q['id']))
    )

@router.callback_query(QuizStates.in_quiz, F.data.startswith("ans_"))
async def handle_quiz_answer(query: CallbackQuery, state: FSMContext):
    selected_option = int(query.data.split("_")[1])
    data = await state.get_data()
    
    q_index = data["current_index"]
    q = data["questions"][q_index]
    
    is_correct = (selected_option == q["correct_option"])
    DBClient.record_answer(query.from_user.id, str(q["id"]), is_correct)
    
    correct_count = data["correct_count"] + (1 if is_correct else 0)
    
    if is_correct:
        await query.answer("✅ Правильно! +15 XP", show_alert=False)
    else:
        correct_ans_text = q['options'][q['correct_option']]
        await query.answer(f"❌ Неправильно. Правильна відповідь: {correct_ans_text}", show_alert=True)

    await state.update_data(
        current_index=q_index + 1,
        correct_count=correct_count
    )

    await send_next_question(query.message, state)

# --- Придбання Premium (Stars & Direct Card) ---

@router.message(F.text.contains("Premium"))
async def show_premium_options(message: Message):
    text = (
        "⭐ **Придбай Premium-доступ до НМТ Англійська:**\n\n"
        "• Повний доступ до всіх тем та розборів\n"
        "• Безлімітна енергія без очікування\n"
        "• Бонусні XP та пріоритет у лідерборді\n\n"
        "Обирай зручний спосіб оплати нижче:"
    )
    await message.answer(text, reply_markup=get_premium_payment_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "buy_premium_stars")
async def send_stars_invoice(query: CallbackQuery):
    await query.answer()
    
    # Створюємо рахунок в Telegram Stars (валюта XTR)
    prices = [LabeledPrice(label="Premium Доступ", amount=250)]
    
    await query.message.answer_invoice(
        title="⭐ НМТ English Premium",
        description="Безлімітна енергія + доступ до всіх матеріалів підготовки!",
        provider_token="",  # Для Stars залишаємо ПУСТТИМ!
        currency="XTR",
        prices=prices,
        start_parameter="premium-stars-buy",
        payload=f"premium_stars_{query.from_user.id}"
    )

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    success = DBClient.set_premium(message.from_user.id)
    if success:
        await message.answer(
            "🎉 **Вітаємо! Оплата пройшла успішно!**\n\nВам надано **Premium-доступ**. Обмеження по енергії знято!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Оплата отримана, але сталася помилка оновлення БД. Зверніться до підтримки.")
