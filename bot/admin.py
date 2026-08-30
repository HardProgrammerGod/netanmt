import asyncio
import logging

from aiogram import F, Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import ADMIN_IDS
from bot.db_client import DBClient
from bot.keyboards import (
    get_admin_category_keyboard,
    get_admin_keyboard,
    get_cancel_keyboard,
)


logger = logging.getLogger(__name__)

admin_router = Router()


class AddTaskFSM(StatesGroup):
    category = State()
    sub_category = State()
    question_text = State()
    options = State()
    correct_answer = State()
    explanation = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message) -> None:
    if not message.from_user:
        return

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Адмін-панель НМТ Англійська</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(F.data == "admin_panel")
async def open_admin_panel(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "🛠 <b>Адмін-панель НМТ Англійська</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(F.data == "admin_add_task")
async def start_add_task(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer()

    await state.set_state(AddTaskFSM.category)

    await callback.message.answer(
        "Оберіть категорію:",
        reply_markup=get_admin_category_keyboard(),
    )


@admin_router.callback_query(
    AddTaskFSM.category,
    F.data.startswith("admin_category:"),
)
async def process_category_callback(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    category = callback.data.split(":", 1)[1]

    await state.update_data(category=category)
    await state.set_state(AddTaskFSM.sub_category)

    await callback.answer()

    await callback.message.answer(
        "Введіть підкатегорію завдання:"
        "\n\nНаприклад: Tenses, Matching, Vocabulary."
        "\n\nАбо введіть <code>-</code>.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@admin_router.message(AddTaskFSM.category)
async def process_category_text(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    category = (message.text or "").strip()

    valid = {
        "Reading",
        "Use of English",
        "Персональний симулятор помилок (190+)",
    }

    if category not in valid:
        await message.answer(
            "⚠️ Оберіть одну з трьох категорій.",
            reply_markup=get_admin_category_keyboard(),
        )
        return

    await state.update_data(category=category)
    await state.set_state(AddTaskFSM.sub_category)

    await message.answer(
        "Введіть підкатегорію:"
    )


@admin_router.message(AddTaskFSM.sub_category)
async def process_sub_category(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    if value == "-":
        value = ""

    if not value:
        value = "General"

    await state.update_data(sub_category=value)
    await state.set_state(AddTaskFSM.question_text)

    await message.answer(
        "Введіть повний текст питання / завдання:"
    )


@admin_router.message(AddTaskFSM.question_text)
async def process_question(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    question = (message.text or "").strip()

    if len(question) < 5:
        await message.answer(
            "⚠️ Текст питання занадто короткий."
        )
        return

    await state.update_data(question_text=question)
    await state.set_state(AddTaskFSM.options)

    await message.answer(
        "Введіть 4 варіанти через кому.\n\n"
        "Приклад:\n"
        "<code>go, went, gone, going</code>",
        parse_mode="HTML",
    )


@admin_router.message(AddTaskFSM.options)
async def process_options(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    raw = message.text or ""

    options = [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]

    if len(options) != 4:
        await message.answer(
            "⚠️ Потрібно рівно 4 варіанти, розділені комами."
        )
        return

    options_dict = {
        "A": options[0],
        "B": options[1],
        "C": options[2],
        "D": options[3],
    }

    await state.update_data(options=options_dict)
    await state.set_state(AddTaskFSM.correct_answer)

    await message.answer(
        "Вкажіть правильну відповідь: "
        "<code>A</code>, <code>B</code>, <code>C</code> або <code>D</code>.",
        parse_mode="HTML",
    )


@admin_router.message(AddTaskFSM.correct_answer)
async def process_correct(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    answer = (message.text or "").strip().upper()

    if answer not in {"A", "B", "C", "D"}:
        await message.answer(
            "⚠️ Введіть тільки A, B, C або D."
        )
        return

    await state.update_data(correct_answer=answer)
    await state.set_state(AddTaskFSM.explanation)

    await message.answer(
        "Введіть пояснення відповіді.\n"
        "Якщо пояснення не потрібне — введіть <code>-</code>.",
        parse_mode="HTML",
    )


@admin_router.message(AddTaskFSM.explanation)
async def process_explanation(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    data = await state.get_data()

    explanation = (message.text or "").strip()

    if explanation == "-":
        explanation = ""

    try:
        await DBClient.add_task(
            category=data["category"],
            sub_category=data["sub_category"],
            section="NMT",
            question_text=data["question_text"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            explanation=explanation,
        )

        await message.answer(
            "✅ <b>Питання успішно додано.</b>",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(),
        )

    except Exception as exc:
        logger.exception(
            "Помилка додавання task: %s",
            exc,
        )

        await message.answer(
            "❌ Не вдалося зберегти питання. "
            "Перевірте лог сервера."
        )

    finally:
        await state.clear()


@admin_router.callback_query(F.data == "admin_cancel")
async def cancel_admin_fsm(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    await state.clear()
    await callback.answer("Скасовано.")

    await callback.message.answer(
        "🛠 Адмін-панель",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer()

    stats = await DBClient.get_admin_stats()

    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Користувачів: <b>{stats['total_users']}</b>\n"
        f"🟢 Активних: <b>{stats['active_users']}</b>\n"
        f"🚫 Неактивних: <b>{stats['blocked_users']}</b>\n"
        f"👑 Premium: <b>{stats['premium_users']}</b>\n"
        f"📚 Питань: <b>{stats['total_questions']}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(F.data == "admin_check_active")
async def admin_check_active(
    callback: CallbackQuery,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer(
        "Аудит запущено."
    )

    await callback.message.edit_text(
        "🔄 <b>Перевіряю активних користувачів...</b>",
        parse_mode="HTML",
    )

    user_ids = await DBClient.get_all_user_ids()

    semaphore = asyncio.Semaphore(20)

    active_count = 0
    blocked_count = 0

    counter_lock = asyncio.Lock()

    async def check_user(user_id: int) -> None:
        nonlocal active_count
        nonlocal blocked_count

        async with semaphore:
            # Не робимо burst із 20 запитів в одну мить.
            await asyncio.sleep(0.05)

            try:
                await callback.bot.send_chat_action(
                    chat_id=user_id,
                    action="typing",
                )

                await DBClient.set_user_active_status(
                    user_id,
                    True,
                )

                async with counter_lock:
                    active_count += 1

            except TelegramForbiddenError:
                await DBClient.set_user_active_status(
                    user_id,
                    False,
                )

                async with counter_lock:
                    blocked_count += 1

            except TelegramRetryAfter as exc:
                logger.warning(
                    "FloodWait для %s: %s сек.",
                    user_id,
                    exc.retry_after,
                )

                await asyncio.sleep(
                    min(float(exc.retry_after), 60.0)
                )

                try:
                    await callback.bot.send_chat_action(
                        chat_id=user_id,
                        action="typing",
                    )

                    await DBClient.set_user_active_status(
                        user_id,
                        True,
                    )

                    async with counter_lock:
                        active_count += 1

                except TelegramForbiddenError:
                    await DBClient.set_user_active_status(
                        user_id,
                        False,
                    )

                    async with counter_lock:
                        blocked_count += 1

                except Exception as retry_exc:
                    logger.warning(
                        "Повторна помилка аудиту %s: %s",
                        user_id,
                        retry_exc,
                    )

            except TelegramBadRequest as exc:
                logger.warning(
                    "TelegramBadRequest для %s: %s",
                    user_id,
                    exc,
                )

            except Exception as exc:
                logger.exception(
                    "Помилка аудиту %s: %s",
                    user_id,
                    exc,
                )

    # Немає прямого послідовного масового циклу.
    await asyncio.gather(
        *(check_user(user_id) for user_id in user_ids)
    )

    await callback.message.edit_text(
        "✅ <b>Аудит завершено</b>\n\n"
        f"🟢 Активних: <b>{active_count}</b>\n"
        f"🚫 Заблокували бота: <b>{blocked_count}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )
