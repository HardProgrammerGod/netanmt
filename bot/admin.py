import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import (
    ADMIN_IDS,
    CATEGORY_PERSONALIZED,
    CATEGORY_READING,
    CATEGORY_USE_OF_ENGLISH,
)
from bot.db_client import DBClient
from bot.keyboards import get_admin_keyboard


logger = logging.getLogger(__name__)

admin_router = Router()


class AddTaskFSM(StatesGroup):
    category = State()
    sub_category = State()
    question_text = State()
    options = State()
    correct_answer = State()
    explanation = State()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message):

    if not message.from_user:
        return

    if not _is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Адмін-панель НМТ Англійська</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(
    callback: CallbackQuery,
):

    if not _is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
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
):

    if not _is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Reading",
                    callback_data="admin_cat_reading",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔤 Use of English",
                    callback_data="admin_cat_use",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Помилки 190+",
                    callback_data="admin_cat_190",
                )
            ],
        ]
    )

    await state.set_state(AddTaskFSM.category)

    await callback.message.answer(
        "Оберіть офіційний блок НМТ:",
        reply_markup=keyboard,
    )


@admin_router.callback_query(
    AddTaskFSM.category,
    F.data.startswith("admin_cat_"),
)
async def process_category_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not _is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
            show_alert=True,
        )
        return

    category_map = {
        "admin_cat_reading": CATEGORY_READING,
        "admin_cat_use": CATEGORY_USE_OF_ENGLISH,
        "admin_cat_190": CATEGORY_PERSONALIZED,
    }

    category = category_map.get(callback.data)

    if not category:
        await callback.answer(
            "Невідома категорія.",
            show_alert=True,
        )
        return

    await state.update_data(
        category=category
    )

    await state.set_state(
        AddTaskFSM.sub_category
    )

    await callback.answer()

    await callback.message.answer(
        "Введіть підкатегорію.\n\n"
        "Наприклад: Tenses, Vocabulary, Matching, "
        "Reading comprehension тощо."
    )


@admin_router.message(AddTaskFSM.category)
async def process_category_text(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    category = message.text.strip()

    allowed = {
        CATEGORY_READING,
        CATEGORY_USE_OF_ENGLISH,
        CATEGORY_PERSONALIZED,
    }

    if category not in allowed:
        await message.answer(
            "⚠️ Використовуйте одну з категорій:\n"
            "• Reading\n"
            "• Use of English\n"
            "• Персональний симулятор помилок"
        )
        return

    await state.update_data(
        category=category
    )

    await state.set_state(
        AddTaskFSM.sub_category
    )

    await message.answer(
        "Введіть підкатегорію:"
    )


@admin_router.message(AddTaskFSM.sub_category)
async def process_sub_category(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    if not value:
        await message.answer(
            "⚠️ Підкатегорія не може бути порожньою."
        )
        return

    await state.update_data(
        sub_category=value
    )

    await state.set_state(
        AddTaskFSM.question_text
    )

    await message.answer(
        "Введіть повний текст питання:"
    )


@admin_router.message(AddTaskFSM.question_text)
async def process_question(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    if not value:
        await message.answer(
            "⚠️ Текст питання не може бути порожнім."
        )
        return

    await state.update_data(
        question_text=value
    )

    await state.set_state(
        AddTaskFSM.options
    )

    await message.answer(
        "Введіть рівно 4 варіанти через кому.\n\n"
        "Приклад:\n"
        "go, went, gone, going"
    )


@admin_router.message(AddTaskFSM.options)
async def process_options(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    raw_options = [
        item.strip()
        for item in (message.text or "").split(",")
        if item.strip()
    ]

    if len(raw_options) != 4:
        await message.answer(
            "⚠️ Потрібно ввести рівно 4 варіанти "
            "через кому."
        )
        return

    options = {
        "A": raw_options[0],
        "B": raw_options[1],
        "C": raw_options[2],
        "D": raw_options[3],
    }

    await state.update_data(
        options=options
    )

    await state.set_state(
        AddTaskFSM.correct_answer
    )

    await message.answer(
        "Вкажіть правильну відповідь:\n"
        "A, B, C або D"
    )


@admin_router.message(AddTaskFSM.correct_answer)
async def process_correct(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    answer = (
        message.text or ""
    ).strip().upper()

    if answer not in {"A", "B", "C", "D"}:
        await message.answer(
            "⚠️ Введіть лише A, B, C або D."
        )
        return

    await state.update_data(
        correct_answer=answer
    )

    await state.set_state(
        AddTaskFSM.explanation
    )

    await message.answer(
        "Введіть пояснення.\n\n"
        "Якщо пояснення не потрібне — введіть '-'."
    )


@admin_router.message(AddTaskFSM.explanation)
async def process_explanation(
    message: Message,
    state: FSMContext,
):

    if not _is_admin(message.from_user.id):
        return

    data = await state.get_data()

    explanation = (
        message.text or ""
    ).strip()

    if explanation == "-":
        explanation = ""

    try:
        task = await DBClient.add_task(
            category=data["category"],
            sub_category=data["sub_category"],
            section="NMT",
            question_text=data["question_text"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            explanation=explanation,
        )

        task_id = task.get("id", "невідомий")

        await message.answer(
            "✅ <b>Питання успішно додано!</b>\n\n"
            f"ID: <code>{task_id}</code>\n"
            f"Блок: <b>{data['category']}</b>\n"
            f"Підкатегорія: <b>{data['sub_category']}</b>",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(),
        )

    except Exception as error:
        logger.exception(
            "Помилка додавання питання."
        )

        await message.answer(
            "❌ Не вдалося зберегти питання.\n"
            "Перевірте логи сервера."
        )

    finally:
        await state.clear()


@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(
    callback: CallbackQuery,
):

    if not _is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer(
        "Збираю статистику..."
    )

    stats = await DBClient.get_admin_stats()

    text = (
        "📊 <b>Статистика NMT English</b>\n\n"
        f"👥 Всього користувачів: "
        f"<b>{stats['total_users']}</b>\n"
        f"🟢 Активних: "
        f"<b>{stats['active_users']}</b>\n"
        f"🚫 Заблокували бота: "
        f"<b>{stats['blocked_users']}</b>\n"
        f"⭐ Premium: "
        f"<b>{stats['premium_users']}</b>\n"
        f"📚 Питань: "
        f"<b>{stats['total_questions']}</b>\n"
        f"🎁 Рефералів: "
        f"<b>{stats['total_referrals']}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.callback_query(
    F.data == "admin_check_active"
)
async def admin_check_active(
    callback: CallbackQuery,
    bot,
):

    if not _is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Доступ заборонено.",
            show_alert=True,
        )
        return

    await callback.answer(
        "⏳ Запускаю аудит..."
    )

    await callback.message.edit_text(
        "🔄 <b>Аудит активності запущено.</b>\n\n"
        "Це може зайняти деякий час.",
        parse_mode="HTML",
    )

    user_ids = await DBClient.get_all_user_ids()

    semaphore = asyncio.Semaphore(20)

    active_count = 0
    blocked_count = 0
    error_count = 0

    active_lock = asyncio.Lock()

    async def check_user(user_id: int):
        nonlocal active_count
        nonlocal blocked_count
        nonlocal error_count

        async with semaphore:

            try:
                await bot.send_chat_action(
                    chat_id=user_id,
                    action="typing",
                )

                await DBClient.set_user_active_status(
                    user_id,
                    True,
                )

                async with active_lock:
                    active_count += 1

            except TelegramForbiddenError:
                await DBClient.set_user_active_status(
                    user_id,
                    False,
                )

                async with active_lock:
                    blocked_count += 1

            except TelegramRetryAfter as error:
                logger.warning(
                    "FloodWait для %s: %s секунд",
                    user_id,
                    error.retry_after,
                )

                await asyncio.sleep(
                    float(error.retry_after)
                )

            except TelegramBadRequest as error:
                logger.warning(
                    "BadRequest для %s: %s",
                    user_id,
                    error,
                )

                await DBClient.set_user_active_status(
                    user_id,
                    False,
                )

                async with active_lock:
                    blocked_count += 1

            except Exception:
                logger.exception(
                    "Помилка аудиту %s",
                    user_id,
                )

                async with active_lock:
                    error_count += 1

            finally:
                await asyncio.sleep(0.05)

    batch_size = 20

    for start in range(
        0,
        len(user_ids),
        batch_size,
    ):
        batch = user_ids[
            start:start + batch_size
        ]

        await asyncio.gather(
            *[
                check_user(user_id)
                for user_id in batch
            ]
        )

    await callback.message.edit_text(
        "✅ <b>Аудит завершено.</b>\n\n"
        f"🟢 Активних: <b>{active_count}</b>\n"
        f"🚫 Заблокували: <b>{blocked_count}</b>\n"
        f"⚠️ Помилок: <b>{error_count}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


# ============================================================
# MANUAL PREMIUM / LAUNCH TOOLS — v1.6
# ============================================================


@admin_router.message(Command("premium"))
async def admin_grant_manual_premium(message: Message, bot: Bot):
    """Usage: /premium <telegram_id> <days>

    Intended for a manager after an alternative/manual payment has been
    verified outside the bot.
    """
    if not message.from_user or not _is_admin(message.from_user.id):
        return

    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer(
            "Формат: <code>/premium TELEGRAM_ID DAYS</code>\n"
            "Наприклад: <code>/premium 123456789 30</code>",
            parse_mode="HTML",
        )
        return

    try:
        target_id = int(parts[1])
        days = int(parts[2])
        if days <= 0 or days > 365:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некоректний Telegram ID або кількість днів.")
        return

    try:
        result = await DBClient.grant_premium(target_id, days)
        await DBClient.mark_manual_payments_completed(target_id)
        await DBClient.log_event(
            target_id,
            "manual_payment_completed",
            {"days": days, "activated_by": message.from_user.id},
        )
        until = result.get("premium_until") or "оновлено"
        await message.answer(
            "✅ <b>Premium активовано.</b>\n\n"
            f"User ID: <code>{target_id}</code>\n"
            f"Днів: <b>{days}</b>\n"
            f"Premium until: <code>{until}</code>",
            parse_mode="HTML",
        )
        try:
            await bot.send_message(
                target_id,
                "⭐ <b>Neta Premium активовано!</b>\n\n"
                f"Доступ додано на <b>{days} днів</b>. "
                "Можеш повертатися до тренувань 🚀",
                parse_mode="HTML",
            )
        except Exception:
            logger.exception("Не вдалося повідомити користувача %s про Premium", target_id)
    except Exception:
        logger.exception("Помилка ручної активації Premium")
        await message.answer("❌ Не вдалося активувати Premium. Перевір логи.")


@admin_router.callback_query(F.data == "admin_launch_waitlist")
async def admin_launch_waitlist(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ заборонено.", show_alert=True)
        return

    await callback.answer()
    try:
        stats = await DBClient.get_launch_waitlist_stats()
    except Exception:
        logger.exception("Не вдалося прочитати launch_waitlist")
        await callback.message.edit_text(
            "⚠️ Таблиця launch_waitlist ще не готова.\n\n"
            "Спочатку запусти SQL v1.6.",
            reply_markup=get_admin_keyboard(),
        )
        return

    await callback.message.edit_text(
        "🚀 <b>Launch / waitlist</b>\n\n"
        f"Усього лідів: <b>{stats['total']}</b>\n"
        f"Готові до пінгу: <b>{stats['ready']}</b>\n"
        f"Вже відправлено: <b>{stats['sent']}</b>\n"
        f"Недоступні/blocked: <b>{stats['blocked']}</b>\n"
        f"Виключено з розсилки: <b>{stats.get('excluded', 0)}</b>\n"
        f"Без Telegram ID: <b>{stats['missing_telegram_id']}</b>\n\n"
        "Перед запуском можна перевірити прев'ю:\n"
        "<code>/launch_preview</code>\n\n"
        "Команда запуску:\n"
        "<code>/launch_ping CONFIRM</code>\n\n"
        "Без слова CONFIRM розсилка не запускається.",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@admin_router.message(Command("waitlist_stats"))
async def admin_waitlist_stats(message: Message):
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    stats = await DBClient.get_launch_waitlist_stats()
    await message.answer(
        "🚀 <b>Waitlist</b>\n\n"
        f"Усього: <b>{stats['total']}</b>\n"
        f"Готові: <b>{stats['ready']}</b>\n"
        f"Відправлено: <b>{stats['sent']}</b>\n"
        f"Blocked: <b>{stats['blocked']}</b>\n"
        f"Виключено: <b>{stats.get('excluded', 0)}</b>\n"
        f"Без Telegram ID: <b>{stats['missing_telegram_id']}</b>",
        parse_mode="HTML",
    )


@admin_router.message(Command("launch_preview"))
async def admin_launch_preview(message: Message, bot: Bot):
    if not message.from_user or not _is_admin(message.from_user.id):
        return

    rows = await DBClient.get_pending_launch_waitlist(limit=200)
    bot_info = await bot.get_me()
    start_url = f"https://t.me/{bot_info.username}?start=launch"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Пройти діагностику",
                url=start_url,
            )
        ]]
    )

    await message.answer(
        "👀 <b>Прев'ю launch-повідомлення</b>\n\n"
        f"Зараз готові до відправки: <b>{len(rows)}</b> людей.\n\n"
        "———\n\n"
        "🚀 <b>Neta NMT відкрито.</b>\n\n"
        "Ти був серед тих, хто залишив ранню заявку на запуск. "
        "Тепер можна пройти 12-завданнєву стартову діагностику, "
        "побачити слабкі теми й одразу отримати персональні тренування.\n\n"
        "Почни з короткої діагностики 👇",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@admin_router.message(Command("launch_ping"))
async def admin_launch_ping(message: Message, bot: Bot):
    if not message.from_user or not _is_admin(message.from_user.id):
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or parts[1].strip().upper() != "CONFIRM":
        await message.answer(
            "⚠️ Розсилку не запущено.\n\n"
            "Якщо точно готовий: <code>/launch_ping CONFIRM</code>",
            parse_mode="HTML",
        )
        return

    rows = await DBClient.get_pending_launch_waitlist(limit=200)
    if not rows:
        await message.answer("Немає лідів, готових до пінгу.")
        return

    bot_info = await bot.get_me()
    start_url = f"https://t.me/{bot_info.username}?start=launch"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🎯 Пройти діагностику", url=start_url)]]
    )

    sent = blocked = failed = 0
    status = await message.answer(
        f"🚀 Запускаю launch-пінг для <b>{len(rows)}</b> лідів...",
        parse_mode="HTML",
    )

    for row in rows:
        telegram_id = int(row["telegram_id"])
        row_id = str(row["id"])
        try:
            await bot.send_message(
                telegram_id,
                "🚀 <b>Neta NMT відкрито.</b>\n\n"
                "Ти був серед тих, хто залишив ранню заявку на запуск. "
                "Тепер можна пройти 12-завданнєву стартову діагностику, "
                "побачити слабкі теми й одразу отримати персональні тренування.\n\n"
                "Почни з короткої діагностики 👇",
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            await DBClient.mark_launch_waitlist_ping(row_id, "sent")
            sent += 1
        except TelegramForbiddenError:
            await DBClient.mark_launch_waitlist_ping(row_id, "blocked")
            blocked += 1
        except TelegramRetryAfter as error:
            await asyncio.sleep(float(error.retry_after) + 0.2)
            try:
                await bot.send_message(
                    telegram_id,
                    "🚀 <b>Neta NMT уже відкрито.</b>\n\n"
                    "Твоя рання заявка активна — переходь до стартової діагностики 👇",
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
                await DBClient.mark_launch_waitlist_ping(row_id, "sent")
                sent += 1
            except Exception:
                failed += 1
        except Exception:
            logger.exception("Launch ping error for %s", telegram_id)
            failed += 1

        await asyncio.sleep(0.08)

    try:
        await status.edit_text(
            "✅ <b>Launch-пінг завершено.</b>\n\n"
            f"Надіслано: <b>{sent}</b>\n"
            f"Blocked: <b>{blocked}</b>\n"
            f"Помилки: <b>{failed}</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass
