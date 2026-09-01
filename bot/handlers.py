import asyncio
import logging
from typing import Any, Dict, List, Optional

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from bot.config import (
    ADMIN_IDS,
    CATEGORY_PERSONALIZED,
    CATEGORY_READING,
    CATEGORY_USE_OF_ENGLISH,
    EXPRESS_QUIZ_LENGTH,
    FREE_DAILY_QUIZ_LIMIT,
    PREMIUM_3_DAYS,
    PREMIUM_3_DAYS_PRICE,
    PREMIUM_30_DAYS,
    PREMIUM_30_DAYS_PRICE,
    REGULAR_QUIZ_LENGTH,
    WEB_APP_URL,
)
from bot.db_client import DBClient
from bot.keyboards import (
    build_referral_share_url,
    get_main_keyboard,
    get_profile_keyboard,
    get_diagnostic_result_keyboard,
    get_question_keyboard,
    get_quiz_categories_keyboard,
    get_referral_keyboard,
    get_tariffs_keyboard,
)


logger = logging.getLogger(__name__)

router = Router()


# ============================================================
# HELPERS
# ============================================================


def _format_options(
    question: Dict[str, Any],
) -> Dict[str, str]:

    raw = question.get("options") or {}

    if isinstance(raw, dict):
        return {
            "A": str(raw.get("A", "")),
            "B": str(raw.get("B", "")),
            "C": str(raw.get("C", "")),
            "D": str(raw.get("D", "")),
        }

    if isinstance(raw, list):
        values = [
            str(item)
            for item in raw
        ]

        return {
            "A": values[0] if len(values) > 0 else "",
            "B": values[1] if len(values) > 1 else "",
            "C": values[2] if len(values) > 2 else "",
            "D": values[3] if len(values) > 3 else "",
        }

    return {
        "A": "",
        "B": "",
        "C": "",
        "D": "",
    }


def _correct_letter(
    question: Dict[str, Any],
) -> str:

    correct = question.get(
        "correct_option",
        0,
    )

    try:
        correct = int(correct)
    except (TypeError, ValueError):
        correct = 0

    letters = (
        "A",
        "B",
        "C",
        "D",
    )

    if 0 <= correct <= 3:
        return letters[correct]

    return "A"

    # Database created by this project uses 0-3.
    if correct in {0, 1, 2, 3}:
        return (
            "A",
            "B",
            "C",
            "D",
        )[correct]

    return "A"


def _diagnostic_range(
    correct: int,
    total: int,
) -> tuple[int, int]:
    """
    Gives a deliberately broad *orientation* range.
    This is not an official NMT score prediction.
    """
    if total <= 0:
        return 100, 119

    ratio = correct / total

    if ratio < 0.25:
        return 100, 119
    if ratio < 0.40:
        return 120, 139
    if ratio < 0.55:
        return 140, 154
    if ratio < 0.70:
        return 155, 169
    if ratio < 0.80:
        return 170, 179
    if ratio < 0.90:
        return 180, 189
    if ratio < 0.97:
        return 190, 195
    return 196, 200


def _diagnostic_weak_topics(
    questions: List[Dict[str, Any]],
    answered_correct: List[bool],
) -> List[Dict[str, Any]]:
    stats: Dict[str, Dict[str, int]] = {}

    for question, is_correct in zip(questions, answered_correct):
        topic = str(
            question.get("sub_category")
            or question.get("category")
            or question.get("topic")
            or "Невизначена тема"
        ).strip()

        item = stats.setdefault(topic, {"correct": 0, "total": 0})
        item["total"] += 1
        if is_correct:
            item["correct"] += 1

    ranked = []
    for topic, item in stats.items():
        accuracy = item["correct"] / max(item["total"], 1)
        ranked.append({
            "topic": topic,
            "correct": item["correct"],
            "total": item["total"],
            "accuracy": round(accuracy, 2),
        })

    ranked.sort(key=lambda x: (x["accuracy"], -x["total"]))
    return ranked[:5]


async def _send_question(
    message: Message,
    question: Dict[str, Any],
    prefix: str = "quiz_answer",
):

    options = _format_options(question)

    question_number = question.get(
        "_number",
        "",
    )

    category = question.get(
        "category",
        question.get("topic", "НМТ"),
    )

    text = (
        f"🧠 <b>{category}</b>\n\n"
    )

    if question_number:
        text += (
            f"Завдання <b>{question_number}</b>\n\n"
        )

    text += (
        f"{question.get('question_text', '')}\n\n"
        "Оберіть відповідь:"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_question_keyboard(
            str(question["id"]),
            options,
            prefix=prefix,
        ),
    )


async def _get_quiz_questions(
    user_id: int,
    category: str,
    limit: int,
) -> List[Dict[str, Any]]:

    if category == CATEGORY_PERSONALIZED:
        return await DBClient.get_personalized_tasks(
            user_id=user_id,
            category=CATEGORY_USE_OF_ENGLISH,
            limit=limit,
        )

    return await DBClient.get_personalized_tasks(
        user_id=user_id,
        category=category,
        limit=limit,
    )


async def _get_diagnostic_questions(
    user_id: int,
) -> List[Dict[str, Any]]:
    """Return the curated 12-question onboarding diagnostic.

    Diagnostic questions are explicitly marked in the DB, so the first
    user experience never depends on the current size/content of the
    regular question pool.
    """
    questions = await DBClient.get_diagnostic_questions(limit=12)

    if len(questions) < 12:
        logger.error(
            "Diagnostic pool has only %s/12 questions. Run the v1.2 SQL seed.",
            len(questions),
        )
        return []

    import random
    random.shuffle(questions)
    return questions[:12]


# ============================================================
# START
# ============================================================


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    bot: Bot,
):

    user = message.from_user

    if not user:
        return

    user_id = user.id

    args = (
        message.text.split(maxsplit=1)[1]
        if message.text and " " in message.text
        else ""
    )

    referrer_id: Optional[int] = None

    if args.startswith("ref_"):
        raw_referrer = args[4:].strip()
        if raw_referrer.isdigit():
            referrer_id = int(raw_referrer)

    existing_result = await DBClient.get_or_create_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        referrer_id=referrer_id,
    )

    await DBClient.record_activity(user_id)

    onboarding_completed = bool(
        existing_result.get("onboarding_completed", False)
    )

    if not onboarding_completed:
        questions = await _get_diagnostic_questions(user_id)

        if questions:
            await _start_quiz(
                message=message,
                user_id=user_id,
                questions=questions,
                title=(
                    "🎯 <b>Швидка діагностика НМТ</b>\n\n"
                    "12 завдань допоможуть визначити твою стартову точку.\n\n"
                    "Після тесту покажемо орієнтовний діапазон результату "
                    "та теми, які варто прокачати першими.\n\n"
                    "Це не офіційний прогноз бала НМТ — лише стартова діагностика.\n\n"
                    "Починаємо 👇"
                ),
                mode="diagnostic",
            )
            return

        # Do not silently skip onboarding if the diagnostic pool is missing.
        # This makes configuration/content problems visible instead of
        # sending a brand-new lead straight into the main menu.
        await message.answer(
            "⚠️ <b>Діагностика ще готується.</b>\n\n"
            "Ми вже працюємо над стартовим тестом. Спробуй відкрити бота трохи пізніше.",
            parse_mode="HTML",
        )
        return

    first_name = user.first_name or "Учень"

    await message.answer(
        f"Вітаю, <b>{first_name}</b>! 👋\n\n"
        "Це персональний тренажер <b>НМТ з англійської мови</b>.\n\n"
        "Тренуй Reading, Use of English та окремо відпрацьовуй помилки, "
        "які заважають рухатися до 190+.\n\n"
        "Обирай дію нижче 👇",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            web_app_url=WEB_APP_URL,
            is_admin=user_id in ADMIN_IDS,
        ),
    )


# ============================================================
# MAIN MENU
# ============================================================


@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(
    callback: CallbackQuery,
):

    await callback.answer()

    await DBClient.record_activity(
        callback.from_user.id
    )

    await callback.message.edit_text(
        "📍 <b>Головне меню</b>\n\n"
        "Готовий зробити ще один крок до 190+?",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            web_app_url=WEB_APP_URL,
            is_admin=callback.from_user.id in ADMIN_IDS,
        ),
    )


# ============================================================
# PROFILE
# ============================================================


@router.callback_query(F.data == "show_profile")
async def cb_show_profile(
    callback: CallbackQuery,
    bot: Bot,
):

    await callback.answer()

    user_id = callback.from_user.id

    user = await DBClient.refresh_premium_status(
        user_id
    )

    await DBClient.record_activity(
        user_id
    )

    bot_info = await bot.get_me()

    ref_link, _ = build_referral_share_url(
        bot_username=bot_info.username,
        user_id=user_id,
    )

    is_premium = bool(
        user.get("is_premium")
    )

    status = (
        "⭐ Premium"
        if is_premium
        else "🆓 Free"
    )

    solved = int(
        user.get("total_tasks_solved") or 0
    )

    streak = int(
        user.get("streak") or 0
    )

    referrals = int(
        user.get("referrals_count") or 0
    )

    premium_until = user.get(
        "premium_until"
    )

    premium_line = ""

    if is_premium and premium_until:
        premium_line = (
            f"\n⏳ Premium до: "
            f"<code>{str(premium_until)[:10]}</code>"
        )

    text = (
        "👤 <b>Твій профіль</b>\n\n"
        f"Статус: <b>{status}</b>"
        f"{premium_line}\n\n"
        f"📚 Розв'язано завдань: "
        f"<b>{solved}</b>\n"
        f"🔥 Streak: <b>{streak} днів</b>\n"
        f"👥 Запрошено друзів: "
        f"<b>{referrals}</b>\n\n"
        "🔗 <b>Твоє реферальне посилання:</b>\n"
        f"<code>{ref_link}</code>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_profile_keyboard(),
    )


# ============================================================
# REFERRALS
# ============================================================


@router.callback_query(F.data == "show_referral")
async def cb_show_referral(
    callback: CallbackQuery,
    bot: Bot,
):

    await callback.answer()

    user_id = callback.from_user.id

    await DBClient.record_activity(
        user_id
    )

    bot_info = await bot.get_me()

    ref_link, share_url = (
        build_referral_share_url(
            bot_username=bot_info.username,
            user_id=user_id,
        )
    )

    user = await DBClient.get_or_create_user(
        user_id=user_id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
    )

    referrals = int(
        user.get("referrals_count") or 0
    )

    text = (
        "🎁 <b>Реферальна програма</b>\n\n"
        "Запроси друга пройти експрес-тест НМТ.\n\n"
        "Коли запрошений друг завершить хоча б "
        "один тест, ти автоматично отримаєш "
        "<b>+3 дні Premium</b>. ⭐\n\n"
        f"👥 Твої запрошення: <b>{referrals}</b>\n\n"
        "🔗 Твоє посилання:\n"
        f"<code>{ref_link}</code>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_referral_keyboard(
            share_url
        ),
    )


# ============================================================
# TARIFFS
# ============================================================


@router.callback_query(F.data == "show_tariffs")
async def cb_show_tariffs(
    callback: CallbackQuery,
):

    await callback.answer()

    await DBClient.record_activity(
        callback.from_user.id
    )

    text = (
        "⭐ <b>Premium для НМТ</b>\n\n"
        "Без зайвих пакетів — обирай потрібний "
        "термін доступу.\n\n"
        f"⭐ <b>3 дні — {PREMIUM_3_DAYS_PRICE} Stars</b>\n"
        "• Premium-доступ\n"
        "• безлімітні тренування\n"
        "• персональний підбір помилок\n\n"
        f"🌟 <b>30 днів — {PREMIUM_30_DAYS_PRICE} Stars</b>\n"
        "• повний Premium на місяць\n"
        "• безлімітні тренування\n"
        "• персональний симулятор помилок\n\n"
        "Оплата проходить прямо через Telegram Stars."
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_tariffs_keyboard(),
    )


# ============================================================
# QUIZ MENU
# ============================================================


@router.callback_query(F.data == "start_quiz_menu")
async def cb_start_quiz_menu(
    callback: CallbackQuery,
):

    await callback.answer()

    await DBClient.record_activity(
        callback.from_user.id
    )

    await callback.message.edit_text(
        "🧠 <b>Тренування НМТ</b>\n\n"
        "Обери блок, який хочеш прокачати:",
        parse_mode="HTML",
        reply_markup=get_quiz_categories_keyboard(),
    )


# ============================================================
# QUIZ START
# ============================================================


async def _start_quiz(
    message: Message,
    user_id: int,
    questions: List[Dict[str, Any]],
    title: str,
    mode: str,
):

    if not questions:
        await message.answer(
            "😔 У цьому розділі поки недостатньо "
            "питань.\n\n"
            "Додай їх через адмін-панель."
        )
        return

    prepared_questions = []

    for index, question in enumerate(
        questions,
        start=1,
    ):
        prepared = dict(question)
        prepared["_number"] = index
        prepared_questions.append(prepared)

    await message.answer(
        title,
        parse_mode="HTML",
    )

    # Для одного користувача quiz state зберігається
    # в FSM MemoryStorage через dispatcher.
    from aiogram.fsm.context import FSMContext

    # Actual state is created in callback handler.
    # Here we attach the data using bot-level temporary storage.
    QUIZ_SESSIONS[user_id] = {
        "questions": prepared_questions,
        "index": 0,
        "correct": 0,
        "answered_correct": [],
        "mode": mode,
        "category": (
            prepared_questions[0].get(
                "category",
                prepared_questions[0].get(
                    "topic",
                    "НМТ",
                ),
            )
        ),
        "referrer_checked": False,
    }

    await _send_question(
        message,
        prepared_questions[0],
        prefix=(
            "diagnostic_answer"
            if mode == "diagnostic"
            else "quiz_answer"
        ),
    )


QUIZ_SESSIONS: Dict[int, Dict[str, Any]] = {}


async def _begin_category_quiz(
    callback: CallbackQuery,
    category: str,
):

    user_id = callback.from_user.id

    can_start = await DBClient.can_start_quiz(
        user_id
    )

    if not can_start:
        await callback.answer(
            "Ліміт Free на сьогодні вичерпано. ⭐",
            show_alert=True,
        )

        await callback.message.edit_text(
            "⭐ <b>Ти використав усі 3 Free-тести на сьогодні.</b>\n\n"
            "Premium відкриває безлімітні тренування.",
            parse_mode="HTML",
            reply_markup=get_tariffs_keyboard(),
        )
        return

    consumed = await DBClient.consume_quiz_attempt(
        user_id
    )

    if not consumed:
        await callback.answer(
            "Ліміт тестів вичерпано.",
            show_alert=True,
        )
        return

    limit = REGULAR_QUIZ_LENGTH

    questions = await _get_quiz_questions(
        user_id=user_id,
        category=category,
        limit=limit,
    )

    if not questions:
        await callback.answer(
            "У цьому розділі поки немає питань.",
            show_alert=True,
        )
        return

    title_map = {
        CATEGORY_READING: (
            "📖 <b>Reading</b>\n\n"
            "Перевіряємо розуміння тексту "
            "та вміння знаходити правильну відповідь."
        ),
        CATEGORY_USE_OF_ENGLISH: (
            "🔤 <b>Use of English</b>\n\n"
            "Працюємо з лексикою, граматикою "
            "та типовими пастками НМТ."
        ),
        CATEGORY_PERSONALIZED: (
            "🎯 <b>Симулятор помилок 190+</b>\n\n"
            "Підбираємо завдання з урахуванням "
            "твоїх попередніх помилок."
        ),
    }

    await callback.answer()

    await _start_quiz(
        message=callback.message,
        user_id=user_id,
        questions=questions,
        title=title_map.get(
            category,
            "🧠 <b>Тест НМТ</b>",
        ),
        mode="regular",
    )


@router.callback_query(F.data == "quiz_cat_reading")
async def quiz_reading(
    callback: CallbackQuery,
):

    await DBClient.record_activity(
        callback.from_user.id
    )

    await _begin_category_quiz(
        callback,
        CATEGORY_READING,
    )


@router.callback_query(
    F.data == "quiz_cat_use_of_english"
)
async def quiz_use_of_english(
    callback: CallbackQuery,
):

    await DBClient.record_activity(
        callback.from_user.id
    )

    await _begin_category_quiz(
        callback,
        CATEGORY_USE_OF_ENGLISH,
    )


@router.callback_query(
    F.data == "quiz_cat_personalized"
)
async def quiz_personalized(
    callback: CallbackQuery,
):

    await DBClient.record_activity(
        callback.from_user.id
    )

    await _begin_category_quiz(
        callback,
        CATEGORY_PERSONALIZED,
    )


# ============================================================
# ANSWERS
# ============================================================


@router.callback_query(
    F.data.startswith("quiz_answer:")
)
@router.callback_query(
    F.data.startswith("diagnostic_answer:")
)
async def process_quiz_answer(
    callback: CallbackQuery,
):

    await callback.answer()

    user_id = callback.from_user.id

    await DBClient.record_activity(
        user_id
    )

    parts = callback.data.split(":")

    if len(parts) != 3:
        return

    _, question_id, selected_letter = parts

    session = QUIZ_SESSIONS.get(
        user_id
    )

    if not session:
        await callback.message.answer(
            "⚠️ Цей тест уже завершено або він застарів.\n"
            "Запусти новий тест."
        )
        return

    questions = session["questions"]
    index = int(session["index"])

    if index >= len(questions):
        return

    question = questions[index]

    if str(question.get("id")) != str(question_id):
        await callback.answer(
            "⚠️ Це питання вже неактуальне.",
            show_alert=True,
        )
        return

    selected_letter = selected_letter.upper()

    correct_letter = _correct_letter(
        question
    )

    is_correct = (
        selected_letter == correct_letter
    )

    if is_correct:
        session["correct"] += 1

    session.setdefault("answered_correct", []).append(is_correct)

    answer_index = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3,
    }.get(
        selected_letter,
        0,
    )

    try:
        await DBClient.save_attempt(
            user_id=user_id,
            question_id=str(question["id"]),
            answer=answer_index,
            is_correct=is_correct,
            count_as_progress=(session.get("mode") != "diagnostic"),
        )
    except Exception:
        logger.exception(
            "Не вдалося зберегти відповідь."
        )

    if is_correct:
        feedback = "✅ <b>Правильно!</b>"
    else:
        feedback = (
            "❌ <b>Не цього разу.</b>\n"
            f"Правильна відповідь: "
            f"<b>{correct_letter}</b>"
        )

    explanation = (
        question.get("explanation") or ""
    ).strip()

    if explanation:
        feedback += (
            f"\n\n💡 {explanation}"
        )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        feedback,
        parse_mode="HTML",
    )

    session["index"] += 1

    if session["index"] >= len(questions):
        await _finish_quiz(
            callback.message,
            user_id,
        )
        return

    next_question = questions[
        session["index"]
    ]

    await _send_question(
        callback.message,
        next_question,
        prefix=(
            "diagnostic_answer"
            if session.get("mode") == "diagnostic"
            else "quiz_answer"
        ),
    )


async def _finish_quiz(
    message: Message,
    user_id: int,
):

    session = QUIZ_SESSIONS.pop(user_id, None)
    if not session:
        return

    correct = int(session["correct"])
    questions = session["questions"]
    total = len(questions)
    mode = session.get("mode", "regular")

    await DBClient.record_activity(user_id)

    if mode == "diagnostic":
        score_min, score_max = _diagnostic_range(correct, total)
        weak_topics = _diagnostic_weak_topics(
            questions,
            session.get("answered_correct", []),
        )

        try:
            await DBClient.save_diagnostic_result(
                user_id=user_id,
                correct=correct,
                total=total,
                score_min=score_min,
                score_max=score_max,
                weak_topics=weak_topics,
            )
        except Exception:
            logger.exception("Не вдалося зберегти результат діагностики.")

        if weak_topics:
            topic_lines = []
            for item in weak_topics[:3]:
                topic_lines.append(
                    f"🔴 {item['topic']} — {item['correct']}/{item['total']}"
                )
            weak_text = "\n".join(topic_lines)
        else:
            weak_text = "🟢 Явних слабких тем поки не виявлено."

        await message.answer(
            "🏁 <b>Діагностику завершено!</b>\n\n"
            f"Правильних: <b>{correct}/{total}</b>\n\n"
            f"🎯 <b>Орієнтовний стартовий діапазон: {score_min}–{score_max}</b>\n\n"
            "Це не офіційний прогноз бала НМТ. Він потрібен, щоб зрозуміти, "
            "з чого тобі краще почати.\n\n"
            "<b>Теми, які зараз варто прокачати:</b>\n"
            f"{weak_text}\n\n"
            "Тепер тренажер може підбирати завдання з урахуванням твоїх результатів.",
            parse_mode="HTML",
            reply_markup=get_diagnostic_result_keyboard(),
        )
        return

    # Referral reward is granted once the invited user completes a regular test.
    referral_rewarded = False
    try:
        user = await DBClient.get_or_create_user(user_id=user_id)
        referrer_id = user.get("referrer_id")
        if referrer_id:
            referral_rewarded = await DBClient.process_referral(
                new_user_id=user_id,
                referrer_id=int(referrer_id),
            )
    except Exception:
        logger.exception("Помилка referral reward.")

    if correct / max(total, 1) >= 0.8:
        conclusion = "🔥 Сильний результат. Тепер працюємо над стабільністю та складними пастками."
    elif correct / max(total, 1) >= 0.6:
        conclusion = "💪 Хороша база. Найбільший резерв — системно закривати помилки."
    else:
        conclusion = "📈 Це лише старт. Кожна помилка підказує, що саме варто прокачати."

    reward_text = (
        "\n\n🎁 <b>Реферальна нагорода активована.</b>"
        if referral_rewarded
        else ""
    )

    await message.answer(
        "🏁 <b>Тренування завершено!</b>\n\n"
        f"Правильних: <b>{correct}/{total}</b>\n\n"
        f"{conclusion}{reward_text}\n\n"
        "Наступне тренування врахує твої попередні помилки.",
        parse_mode="HTML",
        reply_markup=get_quiz_categories_keyboard(),
    )


@router.callback_query(F.data == "start_personalized_after_diagnostic")
async def start_personalized_after_diagnostic(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    questions = await _get_quiz_questions(
        user_id=user_id,
        category=CATEGORY_PERSONALIZED,
        limit=REGULAR_QUIZ_LENGTH,
    )

    if not questions:
        await callback.message.edit_text(
            "🎯 <b>Персональне тренування</b>\n\n"
            "Поки що недостатньо питань, щоб зібрати персональне тренування.\n\n"
            "Спробуй Reading або Use of English нижче.",
            parse_mode="HTML",
            reply_markup=get_quiz_categories_keyboard(),
        )
        return

    can_start = await DBClient.can_start_quiz(user_id)
    if not can_start:
        await callback.message.edit_text(
            "⭐ <b>Free-ліміт на сьогодні вже використано.</b>\n\n"
            "Premium відкриває безлімітні тренування.",
            parse_mode="HTML",
            reply_markup=get_tariffs_keyboard(),
        )
        return

    if not await DBClient.consume_quiz_attempt(user_id):
        return

    await _start_quiz(
        message=callback.message,
        user_id=user_id,
        questions=questions,
        title=(
            "🎯 <b>Твоє перше персональне тренування</b>\n\n"
            "Почнемо зі слабких місць, які виявила діагностика. 👇"
        ),
        mode="regular",
    )


# ============================================================
# STARS
# ============================================================


@router.callback_query(
    F.data == "buy_premium_3days"
)
async def buy_premium_3days(
    callback: CallbackQuery,
    bot: Bot,
):

    await callback.answer()

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="NMT English Premium — 3 дні",
        description=(
            "3 дні Premium-доступу до тренажера НМТ."
        ),
        payload="premium_3days",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Premium 3 дні",
                amount=PREMIUM_3_DAYS_PRICE,
            )
        ],
        provider_token="",
    )


@router.callback_query(
    F.data == "buy_premium_30days"
)
async def buy_premium_30days(
    callback: CallbackQuery,
    bot: Bot,
):

    await callback.answer()

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="NMT English Premium — 30 днів",
        description=(
            "30 днів Premium-доступу до тренажера НМТ."
        ),
        payload="premium_30days",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Premium 30 днів",
                amount=PREMIUM_30_DAYS_PRICE,
            )
        ],
        provider_token="",
    )


@router.pre_checkout_query()
async def process_pre_checkout(
    pre_checkout_query: PreCheckoutQuery,
):

    payload = pre_checkout_query.invoice_payload

    if payload not in {
        "premium_3days",
        "premium_30days",
    }:
        await pre_checkout_query.answer(
            ok=False,
            error_message=(
                "Невідомий платіж."
            ),
        )
        return

    expected_amount = {
        "premium_3days": PREMIUM_3_DAYS_PRICE,
        "premium_30days": PREMIUM_30_DAYS_PRICE,
    }[payload]

    if pre_checkout_query.total_amount != expected_amount:
        await pre_checkout_query.answer(
            ok=False,
            error_message=(
                "Сума платежу не відповідає тарифу."
            ),
        )
        return

    await pre_checkout_query.answer(
        ok=True
    )


@router.message(
    F.successful_payment
)
async def process_successful_payment(
    message: Message,
):

    payment = message.successful_payment

    if not payment:
        return

    payload = payment.invoice_payload

    days_map = {
        "premium_3days": PREMIUM_3_DAYS,
        "premium_30days": PREMIUM_30_DAYS,
    }

    days = days_map.get(payload)

    if not days:
        logger.warning(
            "Невідомий payment payload: %s",
            payload,
        )
        return

    expected_amount = {
        "premium_3days": PREMIUM_3_DAYS_PRICE,
        "premium_30days": PREMIUM_30_DAYS_PRICE,
    }.get(payload)

    if payment.total_amount != expected_amount:
        logger.error(
            "Невідповідна сума Stars: %s",
            payment.total_amount,
        )
        return

    try:
        user = await DBClient.grant_premium(
            user_id=message.from_user.id,
            days=days,
        )

        await DBClient.record_activity(
            message.from_user.id
        )

        premium_until = user.get(
            "premium_until",
            "",
        )

        await message.answer(
            "🎉 <b>Premium активовано!</b>\n\n"
            f"Тривалість: <b>{days} днів</b>\n"
            f"⭐ Оплачено: "
            f"<b>{payment.total_amount} Stars</b>\n\n"
            f"⏳ Premium до: "
            f"<code>{str(premium_until)[:10]}</code>\n\n"
            "Можеш одразу запускати нове тренування.",
            parse_mode="HTML",
            reply_markup=get_quiz_categories_keyboard(),
        )

    except Exception:
        logger.exception(
            "Помилка активації Premium після Stars."
        )

        await message.answer(
            "⚠️ Платіж отримано, але виникла "
            "помилка при активації Premium.\n\n"
            "Адміністратора повідомлено."
        )


# ============================================================
# DAILY RETENTION
# ============================================================


async def daily_retention_loop(
    bot: Bot,
):

    """
    Background retention loop.

    Runs once per hour and finds users who have not
    interacted with the bot for 24+ hours.
    """

    while True:

        try:
            user_ids = (
                await DBClient.get_daily_reminder_candidates(
                    hours=24,
                    limit=100,
                )
            )

            for user_id in user_ids:

                try:
                    question = (
                        await DBClient.get_random_question(
                            category=CATEGORY_USE_OF_ENGLISH
                        )
                    )

                    if not question:
                        continue

                    options = _format_options(
                        question
                    )

                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            "🔥 <b>Твій streak чекає.</b>\n\n"
                            "Одна коротка задача НМТ — "
                            "перевіримо, чи пам'ятаєш правило 👇\n\n"
                            f"{question.get('question_text', '')}"
                        ),
                        parse_mode="HTML",
                        reply_markup=get_question_keyboard(
                            str(question["id"]),
                            options,
                            prefix="daily_answer",
                        ),
                    )

                    await DBClient.mark_reminder_sent(
                        user_id
                    )

                    await asyncio.sleep(
                        0.1
                    )

                except Exception:
                    logger.exception(
                        "Помилка retention reminder для %s",
                        user_id,
                    )

        except Exception:
            logger.exception(
                "Помилка Daily Retention Loop."
            )

        await asyncio.sleep(
            60 * 60
        )


@router.callback_query(
    F.data.startswith("daily_answer:")
)
async def process_daily_answer(
    callback: CallbackQuery,
):

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer()
        return

    _, question_id, selected_letter = parts

    question = None

    try:
        # Для конкретного question_id Supabase search не потрібен:
        # беремо невеликий набір і знаходимо потрібне.
        questions = await DBClient.get_personalized_tasks(
            user_id=callback.from_user.id,
            category=CATEGORY_USE_OF_ENGLISH,
            limit=20,
        )

        for item in questions:
            if str(item.get("id")) == str(question_id):
                question = item
                break

    except Exception:
        logger.exception(
            "Помилка пошуку daily question."
        )

    await callback.answer()

    await DBClient.record_activity(
        callback.from_user.id
    )

    if not question:
        await callback.message.answer(
            "⚠️ Це питання вже недоступне."
        )
        return

    correct = _correct_letter(
        question
    )

    selected = selected_letter.upper()

    if selected == correct:
        text = (
            "🔥 <b>Правильно!</b>\n\n"
            "Streak продовжено. Так тримати."
        )
    else:
        text = (
            "❌ <b>Не вгадав.</b>\n\n"
            f"Правильна відповідь: <b>{correct}</b>"
        )

        explanation = (
            question.get("explanation") or ""
        ).strip()

        if explanation:
            text += (
                f"\n\n💡 {explanation}"
            )

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await callback.message.answer(
        text,
        parse_mode="HTML",
    )
