"""Segmented, persisted retention messages for Neta learning sessions."""

import asyncio
import html
import logging
from typing import Any, Dict, Optional, Tuple

from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards import get_question_keyboard

logger = logging.getLogger(__name__)
LETTERS = ("A", "B", "C", "D")
# Kept for compatibility with the v10 offline test/import surface. v12 copy is
# selected by persisted segment + variant instead of rotating generic tips.
TIPS = tuple(f"v10-tip-{index}" for index in range(30))


def _payload(delivery: Dict[str, Any]) -> Dict[str, Any]:
    value = delivery.get("payload") or {}
    return value if isinstance(value, dict) else {}


def _footer(delivery_id: str, button_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data=f"reminder_go:{delivery_id}")],
        [
            InlineKeyboardButton(text="⚙️ Час", callback_data="show_settings"),
            InlineKeyboardButton(text="Без нагадувань", callback_data="reminder_off"),
        ],
    ])


def _question_text(question: Dict[str, Any], index: int, total: int) -> str:
    options = question.get("options") or {}
    if isinstance(options, list):
        options = {
            letter: str(options[position]) if position < len(options) else ""
            for position, letter in enumerate(LETTERS)
        }
    elif isinstance(options, dict):
        options = {letter: str(options.get(letter, "")) for letter in LETTERS}
    else:
        options = {letter: "" for letter in LETTERS}

    option_lines = "\n".join(
        f"<b>{letter}.</b> {html.escape(options.get(letter, ''))}"
        for letter in LETTERS
    )
    body = html.escape(str(question.get("question_text") or ""))
    return f"<b>{index + 1} із {total}</b>\n\n{body}\n\n{option_lines}"


def reminder_message(
    delivery: Dict[str, Any],
    question_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, InlineKeyboardMarkup]:
    """Build copy and CTA from the segment persisted before delivery."""
    delivery_id = str(delivery["id"])
    segment = str(delivery.get("segment") or "daily_ready")
    variant = str(delivery.get("variant") or "a")
    payload = _payload(delivery)

    if segment == "abandoned":
        answered = max(0, int(payload.get("answered_count") or 0))
        total = max(answered + 1, int(payload.get("total") or 0))
        if variant == "b":
            text = (
                "<b>Твій прогрес збережено</b>\n\n"
                f"Уже готово <b>{answered}/{total}</b>. Продовжимо саме з того питання, де ти зупинився — спочатку нічого проходити не треба."
            )
        else:
            text = (
                "<b>Залишилося зовсім трохи</b>\n\n"
                f"Ти вже виконав <b>{answered}/{total}</b>. Neta зберегла відповіді й відкриє наступне питання."
            )
        return text, _footer(delivery_id, "▶️ Продовжити з місця зупинки")

    if segment == "daily_errors":
        focus = html.escape(str(payload.get("focus_skill") or "сьогоднішні помилки"))
        if variant == "b":
            text = (
                "<b>Neta Memory знайшла, що повторити</b>\n\n"
                f"Фокус: <b>{focus}</b>. П'ять коротких питань допоможуть не повторити цю помилку на НМТ."
            )
        else:
            text = (
                "<b>Одна слабка тема вже чекає</b>\n\n"
                f"Neta повернула в повторення: <b>{focus}</b>. Закріплення займе приблизно 4 хвилини."
            )
        return text, _footer(delivery_id, "🧠 Закріпити помилки · 5")

    if segment == "first_question" and question_context:
        session = question_context["session"]
        question = question_context["question"]
        index = int(session.get("current_index") or 0)
        total = len(session.get("question_ids") or [])
        opening = (
            "<b>Перевір себе одним питанням</b>\n\nОбери A, B, C або D — без реєстрацій і довгого тесту."
            if variant == "b"
            else
            "<b>Спробуй Neta прямо тут</b>\n\nОдне коротке питання. Після відповіді одразу отримаєш пояснення."
        )
        text = f"{opening}\n\n{_question_text(question, index, total)}"
        question_keyboard = get_question_keyboard(
            str(session["id"]), index, question.get("options") or {}
        )
        rows = list(question_keyboard.inline_keyboard)
        rows.append([
            InlineKeyboardButton(text="⚙️ Час", callback_data="show_settings"),
            InlineKeyboardButton(text="Без нагадувань", callback_data="reminder_off"),
        ])
        return text, InlineKeyboardMarkup(inline_keyboard=rows)

    if segment == "reactivation":
        if variant == "b":
            text = (
                "<b>Повернемо англійську без марафону?</b>\n\n"
                "Neta підбере коротке заняття за твоєю історією. Три-чотири хвилини — і на сьогодні достатньо."
            )
        else:
            text = (
                "<b>Твій прогрес у Neta збережено</b>\n\n"
                "Повернися на одне коротке заняття: бот дасть не випадкові вправи, а те, що зараз корисніше повторити."
            )
        return text, _footer(delivery_id, "⚡ Повернутися на 4 хв")

    if variant == "b":
        text = (
            "<b>Daily уже готовий</b>\n\n"
            "4 питання: одне повторення, один слабкий сигнал і нові завдання. Без довгого тесту."
        )
    else:
        text = (
            "<b>Сьогоднішні 4 питання готові</b>\n\n"
            "Neta змішала нове з тим, що тобі варто повторити. Це приблизно 4 хвилини."
        )
    return text, _footer(delivery_id, "⚡ Почати Daily · 4")


async def _prepare_first_question(
    delivery: Dict[str, Any], db: Any
) -> Optional[Dict[str, Any]]:
    if str(delivery.get("segment") or "") != "first_question":
        return None

    user_id = int(delivery["user_id"])
    session = await db.get_or_create_session(user_id, "intro", 3)
    if str(session.get("status") or "") != "active":
        return None

    question_ids = [str(value) for value in (session.get("question_ids") or [])]
    index = int(session.get("current_index") or 0)
    if index < 0 or index >= len(question_ids):
        return None

    questions = await db.get_questions(question_ids)
    if len(questions) != len(question_ids):
        return None

    await db.attach_reminder_session(
        str(delivery["id"]), user_id, str(session["id"]), "intro"
    )
    delivery["target_session_id"] = str(session["id"])
    delivery["target_action"] = "intro"
    return {"session": session, "question": questions[index]}


async def send_reminder_batch(bot: Any, db: Any) -> int:
    """Claim before send so concurrent workers and restarts cannot duplicate."""
    deliveries = await db.claim_reminders()
    for delivery in deliveries:
        user_id = int(delivery["user_id"])
        delivery_id = str(delivery["id"])
        try:
            if not await db.can_send_reminder(delivery_id):
                await db.finish_reminder(delivery_id, "skipped")
                continue

            question_context = await _prepare_first_question(delivery, db)
            if str(delivery.get("segment") or "") == "first_question" and not question_context:
                await db.finish_reminder(delivery_id, "skipped")
                continue

            text, keyboard = reminder_message(delivery, question_context)
            await bot.send_message(user_id, text, reply_markup=keyboard)
        except TelegramForbiddenError:
            await db.finish_reminder(delivery_id, "blocked")
            await db.set_user_inactive(user_id)
        except TelegramRetryAfter as exc:
            await db.finish_reminder(delivery_id, "failed")
            return max(60, int(exc.retry_after))
        except Exception:
            logger.exception("Reminder send uncertain/failed for %s", user_id)
            await db.finish_reminder(delivery_id, "failed")
        else:
            await db.finish_reminder(delivery_id, "sent")
            try:
                await db.mark_reminder_sent(user_id)
            except Exception:
                logger.exception("Could not update last_reminder_at for %s", user_id)
            if question_context:
                session = question_context["session"]
                index = int(session.get("current_index") or 0)
                try:
                    await db.log_event(
                        user_id,
                        "question_shown",
                        {
                            "session_id": str(session["id"]),
                            "question_index": index,
                            "session_type": "intro",
                            "source": "retention_first_question",
                            "delivery_id": delivery_id,
                        },
                        event_key=f"shown:{session['id']}:{index}",
                    )
                except Exception:
                    logger.exception("Could not log inline reminder question")
        await asyncio.sleep(0.08)
    return 60
