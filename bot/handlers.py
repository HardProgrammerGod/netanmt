import asyncio
import logging
from typing import Any, Optional

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from bot.config import (
    ADMIN_IDS,
    EXPRESS_TEST_LENGTH,
    FREE_DAILY_TESTS,
    PREMIUM_3_DAYS,
    PREMIUM_30_DAYS,
    REFERRAL_PREMIUM_DAYS,
    STARS_3_DAYS,
    STARS_30_DAYS,
    WEB_APP_URL,
)
from bot.db_client import DBClient
from bot.keyboards import (
    get_answer_keyboard,
    get_main_keyboard,
    get_profile_keyboard,
    get_quiz_categories_keyboard,
    get_retention_answer_keyboard,
    get_tariffs_keyboard,
)


logger = logging.getLogger(__name__)

router = Router()


class QuizFSM(StatesGroup):
    mode = State()
    category = State()
    tasks = State()
    current_index = State()
    score = State()


def parse_referrer(message: Message) -> Optional[int]:
    if not message.text:
        return None

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        return None

    parameter = parts[1].strip()

    if not parameter.startswith("ref_"):
        return None

    raw_id = parameter[4:]

    if not raw_id.isdigit():
        return None

    return int(raw_id)


async def send_main_menu(
    message: Message,
    user_id: int,
) -> None:
    await message.answer(
        "📍 <b>Головне меню</b>\n\n"
        "Тренуй саме ті блоки НМТ, які зараз потрібні.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            web_app_url=WEB_APP_URL,
            is_admin=user_id in ADMIN_IDS,
        ),
    )


async def get_task_by_id(
    task_id: int,
) -> Optional[dict[str, Any]]:
    """
    Отримує конкретне питання.

    Метод окремий, щоб callback не залежав від стану
    після рестарту процесу.
    """

    # Невеликий hack не потрібен: персоналізований вибір
    # виконується до початку тесту, а всі task objects
    # зберігаються у FSM.
    return None


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    referrer_id = parse_referrer(message)

    user = await DBClient.get_or_create_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referrer_id=referrer_id,
    )

    if user.get("_is_new") and referrer_id:
        await DBClient.process_referral(
            new_user_id=user_id,
            referrer_id=referrer_id,
        )

    if user.get("_is_new"):
        await message.answer(
            f"Привіт, <b>{message.from_user.first_name}</b>! 👋\n\n"
            "Не будемо витрачати час на довгі анкети.\n"
            "Зараз дам тобі <b>5 коротких завдань НМТ</b>, "
            "а після них покажу орієнтовну стартову оцінку.\n\n"
            "Готовий? 🚀",
            parse_mode="HTML",
        )

        await start_express_test(
            message=message,
            state=state,
        )
        return

    await message.answer(
        f"З поверненням, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Продовжуємо підготовку?",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            web_app_url=WEB_APP_URL,
            is_admin=user_id in ADMIN_IDS,
        ),
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()
    await callback.answer()

    await callback.message.edit_text(
        "📍 <b>Головне меню</b>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            web_app_url=WEB_APP_URL,
            is_admin=callback.from_user.id in ADMIN_IDS,
        ),
    )


async def start_express_test(
    message: Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id

    allowed = await DBClient.consume_test(user_id)

    if not allowed:
        await message.answer(
            "На сьогодні безкоштовні спроби вже використані.\n"
            "У Premium лімітів на тести немає.",
            reply_markup=get_tariffs_keyboard(),
        )
        return

    tasks = await DBClient.get_express_tasks(
        limit=EXPRESS_TEST_LENGTH,
    )

    if len(tasks) < 3:
        await message.answer(
            "⚠️ У базі поки недостатньо питань для експрес-тесту."
        )
        return

    tasks = tasks[:EXPRESS_TEST_LENGTH]

    await state.set_state(QuizFSM.mode)

    await state.update_data(
        mode="express",
        category="express",
        tasks=tasks,
        current_index=0,
        score=0,
    )

    await send_current_question(
        message=message,
        state=state,
    )


@router.callback_query(F.data == "start_quiz_menu")
async def quiz_menu(
    callback: CallbackQuery,
) -> None:
    await callback.answer()

    await callback.message.edit_text(
        "🧠 <b>Обери формат тренування</b>",
        parse_mode="HTML",
        reply_markup=get_quiz_categories_keyboard(),
    )


async def start_category_test(
    callback: CallbackQuery,
    state: FSMContext,
    category: str,
) -> None:
    user_id = callback.from_user.id

    user = await DBClient.get_or_create_user(
        user_id=user_id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
    )

    if not user.get("is_premium"):
        allowed = await DBClient.consume_test(user_id)

        if not allowed:
            await callback.answer(
                "Безкоштовні спроби на сьогодні закінчилися.",
                show_alert=True,
            )

            await callback.message.edit_text(
                "👑 <b>Хочеш більше практики?</b>\n\n"
                "Premium прибирає денний ліміт і відкриває "
                "персональне тренування.",
                parse_mode="HTML",
                reply_markup=get_tariffs_keyboard(),
            )
            return

    tasks = await DBClient.get_personalized_tasks(
        user_id=user_id,
        category=category,
        limit=5,
    )

    if not tasks:
        await callback.answer(
            "Поки немає питань у цьому розділі.",
            show_alert=True,
        )
        return

    await state.set_state(QuizFSM.mode)

    await state.update_data(
        mode="category",
        category=category,
        tasks=tasks,
        current_index=0,
        score=0,
    )

    await callback.answer()

    await callback.message.edit_text(
        f"🚀 <b>{category}</b>\n\n"
        "Відповідай на кожне питання. "
        "Після завершення покажу результат.",
        parse_mode="HTML",
    )

    await send_current_question(
        message=callback.message,
        state=state,
    )


@router.callback_query(F.data == "quiz_cat_reading")
async def quiz_reading(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await start_category_test(
        callback,
        state,
        "Reading",
    )


@router.callback_query(F.data == "quiz_cat_use_of_english")
async def quiz_use_of_english(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await start_category_test(
        callback,
        state,
        "Use of English",
    )


@router.callback_query(F.data == "quiz_cat_personalized")
async def quiz_personalized(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await start_category_test(
        callback,
        state,
        "personalized",
    )


async def send_current_question(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    tasks = data.get("tasks") or []
    current_index = int(data.get("current_index", 0))

    if current_index >= len(tasks):
        await finish_quiz(
            message=message,
            state=state,
        )
        return

    task = tasks[current_index]

    options = task.get("options") or {}

    category = task.get("category", "НМТ")

    text = (
        f"📝 <b>Питання {current_index + 1}/{len(tasks)}</b>\n"
        f"Розділ: <b>{category}</b>\n\n"
        f"{task.get('question_text', '')}"
    )

    try:
        await message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_answer_keyboard(
                int(task["id"]),
                options,
            ),
        )
    except TelegramBadRequest:
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_answer_keyboard(
                int(task["id"]),
                options,
            ),
        )


@router.callback_query(F.data.startswith("quiz_answer:"))
async def quiz_answer(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer("Некоректна відповідь.", show_alert=True)
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        await callback.answer("Некоректне питання.", show_alert=True)
        return

    answer = parts[2].upper()

    if answer not in {"A", "B", "C", "D"}:
        await callback.answer("Некоректна відповідь.", show_alert=True)
        return

    data = await state.get_data()

    tasks = data.get("tasks") or []
    current_index = int(data.get("current_index", 0))
    score = int(data.get("score", 0))

    if current_index >= len(tasks):
        await callback.answer("Тест вже завершено.")
        return

    task = tasks[current_index]

    if int(task["id"]) != task_id:
        await callback.answer(
            "Це питання вже неактивне.",
            show_alert=False,
        )
        return

    correct_answer = str(
        task.get("correct_answer", "")
    ).upper()

    is_correct = answer == correct_answer

    if is_correct:
        score += 1

    await DBClient.save_attempt(
        user_id=callback.from_user.id,
        task_id=task_id,
        answer=answer,
        is_correct=is_correct,
    )

    await state.update_data(
        score=score,
        current_index=current_index + 1,
    )

    await callback.answer(
        "✅ Правильно!" if is_correct else "❌ Помилка."
    )

    if not is_correct and task.get("explanation"):
        await callback.message.answer(
            "💡 <b>Розбір:</b>\n"
            f"{task['explanation']}",
            parse_mode="HTML",
        )

    await send_current_question(
        message=callback.message,
        state=state,
    )


async def finish_quiz(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    tasks = data.get("tasks") or []
    score = int(data.get("score", 0))
    total = len(tasks)

    if total <= 0:
        await state.clear()
        return

    score_200 = round(
        (score / total) * 200
    )

    await DBClient.complete_test(
        message.chat.id,
    )

    referrer_id = await DBClient.complete_referral(
        message.chat.id,
    )

    if referrer_id:
        try:
            await message.bot.send_message(
                referrer_id,
                "🎉 <b>Твій друг завершив перший тест!</b>\n\n"
                f"Ти отримав <b>+{REFERRAL_PREMIUM_DAYS} дні Premium</b> "
                "за запрошення.",
                parse_mode="HTML",
            )
        except Exception as exc:
            logger.warning(
                "Не вдалося повідомити реферера %s: %s",
                referrer_id,
                exc,
            )

    mode = data.get("mode")

    if mode == "express":
        text = (
            "🎯 <b>Експрес-тест завершено!</b>\n\n"
            f"Результат: <b>{score}/{total}</b>\n\n"
            f"Твій орієнтовний стартовий бал: "
            f"<b>{score_200}/200</b>.\n\n"
            "Це не офіційний перерахунок НМТ, а стартова "
            "оцінка для тренажера.\n\n"
            "Хочеш рухатися до <b>180+</b>? "
            "Переходь до персонального тренування."
        )
    else:
        text = (
            "🏁 <b>Тест завершено!</b>\n\n"
            f"Правильних: <b>{score}/{total}</b>\n"
            f"Орієнтовний результат: <b>{score_200}/200</b>\n\n"
            "Наступний крок — повторити питання, "
            "де були помилки."
        )

    await state.clear()

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_quiz_categories_keyboard(),
    )


@router.callback_query(F.data == "show_profile")
async def show_profile(
    callback: CallbackQuery,
) -> None:
    await callback.answer()

    user = await DBClient.get_user_profile(
        callback.from_user.id,
    )

    premium_until = user.get("premium_until")

    if user.get("is_premium") and premium_until:
        status = f"👑 Premium до <b>{premium_until[:10]}</b>"
    elif user.get("is_premium"):
        status = "👑 Premium"
    else:
        status = "👤 Free"

    text = (
        "👤 <b>Твій профіль</b>\n\n"
        f"Статус: {status}\n"
        f"📚 Розв'язано завдань: "
        f"<b>{int(user.get('total_tasks_solved') or 0)}</b>\n"
        f"🔥 Streak: "
        f"<b>{int(user.get('streak') or 0)} днів</b>\n"
        f"🎯 Завершено тестів: "
        f"<b>{int(user.get('total_tests_passed') or 0)}</b>\n"
        f"👥 Запрошено друзів: "
        f"<b>{int(user.get('referrals_count') or 0)}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_profile_keyboard(),
    )


@router.callback_query(F.data == "show_referral")
async def show_referral(
    callback: CallbackQuery,
    bot: Bot,
) -> None:
    await callback.answer()

    me = await bot.get_me()

    link = (
        f"https://t.me/{me.username}"
        f"?start=ref_{callback.from_user.id}"
    )

    user = await DBClient.get_user_profile(
        callback.from_user.id,
    )

    share_text = (
        "🔥 Я готуюся до НМТ з англійської тут.\n"
        "Спробуй короткий тест і подивись свій результат 👇"
    )

    share_url = (
        "https://t.me/share/url"
        f"?url={link}"
        f"&text={share_text}"
    )

    text = (
        "🎁 <b>Реферальна програма</b>\n\n"
        f"Запрошуй друзів за своїм посиланням.\n"
        f"Коли запрошений друг завершить перший тест, "
        f"ти отримаєш <b>+{REFERRAL_PREMIUM_DAYS} дні Premium</b>.\n\n"
        f"👥 Твої запрошені друзі: "
        f"<b>{int(user.get('referrals_count') or 0)}</b>\n\n"
        f"🔗 <code>{link}</code>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                {
                    "text": "📤 Поділитися",
                    "url": share_url,
                }
            ],
            [
                {
                    "text": "⬅️ Профіль",
                    "callback_data": "show_profile",
                }
            ],
        ]
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "show_tariffs")
async def show_tariffs(
    callback: CallbackQuery,
) -> None:
    await callback.answer()

    text = (
        "👑 <b>Premium</b>\n\n"
        "Для тих, хто хоче тренуватися без денного ліміту "
        "та системно працювати над помилками.\n\n"
        f"⭐ <b>{STARS_3_DAYS}</b> — 3 дні\n"
        f"⭐ <b>{STARS_30_DAYS}</b> — 30 днів\n\n"
        "Оплата проходить безпосередньо через Telegram Stars."
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_tariffs_keyboard(),
    )


async def send_stars_invoice(
    callback: CallbackQuery,
    days: int,
    stars: int,
) -> None:
    payload = f"premium_{days}days"

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"NMT Premium — {days} дні",
        description=(
            "Персональне тренування НМТ, "
            "безлімітні тести та робота над помилками."
        ),
        payload=payload,
        currency="XTR",
        prices=[
            LabeledPrice(
                label=f"Premium {days} дні",
                amount=stars,
            )
        ],
        provider_token="",
        start_parameter=payload,
    )


@router.callback_query(F.data == "buy_premium_3days")
async def buy_premium_3days(
    callback: CallbackQuery,
) -> None:
    await callback.answer()

    await send_stars_invoice(
        callback=callback,
        days=PREMIUM_3_DAYS,
        stars=STARS_3_DAYS,
    )


@router.callback_query(F.data == "buy_premium_30days")
async def buy_premium_30days(
    callback: CallbackQuery,
) -> None:
    await callback.answer()

    await send_stars_invoice(
        callback=callback,
        days=PREMIUM_30_DAYS,
        stars=STARS_30_DAYS,
    )


@router.pre_checkout_query()
async def process_pre_checkout(
    pre_checkout_query: PreCheckoutQuery,
) -> None:
    payload = pre_checkout_query.invoice_payload

    if payload not in {
        "premium_3days",
        "premium_30days",
    }:
        await pre_checkout_query.answer(
            ok=False,
            error_message="Невідомий тариф.",
        )
        return

    expected_amount = {
        "premium_3days": STARS_3_DAYS,
        "premium_30days": STARS_30_DAYS,
    }[payload]

    if pre_checkout_query.total_amount != expected_amount:
        await pre_checkout_query.answer(
            ok=False,
            error_message="Сума рахунку не відповідає тарифу.",
        )
        return

    await pre_checkout_query.answer(
        ok=True,
    )


@router.message(F.successful_payment)
async def process_successful_payment(
    message: Message,
) -> None:
    payment = message.successful_payment

    if payment is None:
        return

    payload = payment.invoice_payload

    plan_days = {
        "premium_3days": PREMIUM_3_DAYS,
        "premium_30days": PREMIUM_30_DAYS,
    }.get(payload)

    if plan_days is None:
        logger.error(
            "Unknown successful payment payload: %s",
            payload,
        )
        return

    registered = await DBClient.register_payment(
        user_id=message.from_user.id,
        payload=payload,
        charge_id=payment.telegram_payment_charge_id,
        amount=payment.total_amount,
    )

    if not registered:
        await message.answer(
            "ℹ️ Цей платіж уже був оброблений."
        )
        return

    premium_until = await DBClient.grant_premium(
        user_id=message.from_user.id,
        days=plan_days,
    )

    until_text = (
        premium_until.strftime("%d.%m.%Y")
        if premium_until
        else "активовано"
    )

    await message.answer(
        "🎉 <b>Premium активовано!</b>\n\n"
        f"Термін: <b>{plan_days} дні</b>\n"
        f"Активний до: <b>{until_text}</b>\n\n"
        "Можеш одразу запускати персональне тренування 🚀",
        parse_mode="HTML",
        reply_markup=get_quiz_categories_keyboard(),
    )


@router.message(Command("admin"))
async def admin_command(
    message: Message,
) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "⚡ <b>Адмін-панель</b>",
        parse_mode="HTML",
    )
