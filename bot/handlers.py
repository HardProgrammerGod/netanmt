import asyncio
import html
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery

from bot.config import ADMIN_IDS, CHANNEL_URL, PREMIUM_3_DAYS, PREMIUM_3_DAYS_PRICE, PREMIUM_30_DAYS, PREMIUM_30_DAYS_PRICE
from bot.db_client import DBClient
from bot.learning_db import LearningDB, skill_name
from bot.keyboards import (
    build_referral_share_url,
    get_back_keyboard,
    get_channel_keyboard,
    get_course_keyboard,
    get_daily_result_keyboard,
    get_diagnostic_result_keyboard,
    get_friends_keyboard,
    get_intro_result_keyboard,
    get_main_keyboard,
    get_practice_picker_keyboard,
    get_practice_result_keyboard,
    get_progress_keyboard,
    get_privacy_keyboard,
    get_question_keyboard,
    get_reminder_offer_keyboard,
    get_settings_keyboard,
    get_start_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()
KYIV = ZoneInfo("Europe/Kyiv")
LETTERS = ("A", "B", "C", "D")


def _background(coro) -> None:
    task = asyncio.create_task(coro)
    task.add_done_callback(lambda t: logger.error("Background task failed", exc_info=t.exception()) if (not t.cancelled() and t.exception()) else None)


def _options(question: Dict[str, Any]) -> Dict[str, str]:
    raw = question.get("options") or {}
    if isinstance(raw, dict):
        return {letter: str(raw.get(letter, "")) for letter in LETTERS}
    if isinstance(raw, list):
        return {letter: str(raw[i]) if i < len(raw) else "" for i, letter in enumerate(LETTERS)}
    return {letter: "" for letter in LETTERS}


def _correct_index(question: Dict[str, Any]) -> int:
    try:
        value = int(question.get("correct_option", 0))
    except (TypeError, ValueError):
        return 0
    return value if 0 <= value <= 3 else 0


def _question_text(question: Dict[str, Any], index: int, total: int, prefix: Optional[str] = None) -> str:
    skill = html.escape(skill_name(question))
    body = html.escape(str(question.get("question_text") or ""))
    options = _options(question)
    option_lines = "\n".join(
        f"<b>{letter}.</b> {html.escape(options.get(letter, ''))}"
        for letter in LETTERS
    )
    head = f"<b>{index + 1} із {total} · {skill}</b>"
    parts = []
    if prefix:
        parts.append(prefix)
    parts.extend([head, body, option_lines])
    return "\n\n".join(part for part in parts if part)


async def _main_screen(message: Message, user_id: int, edit: bool = False) -> None:
    daily_session = None
    try:
        daily_session = await LearningDB.get_today_daily_session(user_id)
    except Exception:
        logger.exception("Could not read daily status")

    done = bool(daily_session)
    had_errors = False
    if done:
        total = len(daily_session.get("question_ids") or [])
        correct = int(daily_session.get("correct_count") or 0)
        had_errors = correct < total
        focus_line = ""
        if had_errors:
            try:
                insights = await LearningDB.get_session_insights(str(daily_session.get("id")), user_id)
                weak = [x for x in (insights.get("focus") or []) if int(x.get("accuracy") or 0) < 100]
                if weak:
                    focus_line = html.escape(str(weak[0].get("skill") or "цю тему"))
            except Exception:
                logger.exception("Could not build Daily focus for main screen")
        if had_errors:
            memory_text = (
                f"Ти помилився у темі <b>{focus_line}</b>. Neta додала її до повторення."
                if focus_line else
                "Neta додала сьогоднішні помилки до повторення."
            )
            continue_text = "Можеш закріпити їх зараз або повернутися завтра."
        else:
            memory_text = "Сьогодні без помилок. Neta може дати складніший короткий блок."
            continue_text = "Можеш підняти складність зараз або повернутися завтра."
        text = (
            "<b>⚡ Daily завершено</b>\n\n"
            f"Результат: <b>{correct}/{total}</b> ✅\n"
            f"{memory_text}\n\n"
            f"{continue_text}"
        )
    else:
        text = (
            "<b>⚡ Neta Daily</b>\n\n"
            "<b>4 питання · ~4 хв</b>\n"
            "Короткий мінімум на сьогодні: нове + те, що Neta Memory повернула на повторення."
        )

    markup = get_main_keyboard(
        daily_completed=done,
        had_daily_errors=had_errors,
        is_admin=user_id in ADMIN_IDS,
    )
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def _load_session_questions(session: Dict[str, Any]) -> List[Dict[str, Any]]:
    ids = [str(x) for x in (session.get("question_ids") or [])]
    rows = await LearningDB.get_questions(ids)
    if len(rows) != len(ids):
        raise RuntimeError(f"Session question mismatch: expected {len(ids)}, got {len(rows)}")
    return rows


async def _send_current_question(message: Message, session: Dict[str, Any], intro: bool = False) -> None:
    questions = await _load_session_questions(session)
    index = int(session.get("current_index") or 0)
    total = len(questions)
    if session.get("status") == "completed" or index >= total:
        await _send_session_result(message, session)
        return
    q = questions[index]
    session_type = str(session.get("session_type") or "daily")
    prefix = None
    if session_type == "intro" and index == 0:
        prefix = "Три питання — і Neta покаже перші сигнали: що вже виходить і що варто повернути в повторення."
    elif session_type == "diagnostic" and index == 0:
        prefix = "Карта навичок · 12 питань. Це не прогноз бала НМТ і не офіційна оцінка рівня."
    await message.answer(
        _question_text(q, index, total, prefix),
        reply_markup=get_question_keyboard(str(session["id"]), index, _options(q)),
    )
    _background(LearningDB.log_event(
        int(session["user_id"]),
        "question_shown",
        {"session_id": str(session["id"]), "question_index": index, "session_type": session_type},
        event_key=f"shown:{session['id']}:{index}",
    ))


async def _send_session_result(message: Message, session: Dict[str, Any]) -> None:
    total = len(session.get("question_ids") or [])
    correct = int(session.get("correct_count") or 0)
    session_type = str(session.get("session_type") or "daily")
    accuracy = round(correct / total * 100) if total else 0
    try:
        insights = await LearningDB.get_session_insights(str(session.get("id")), int(session.get("user_id")))
    except Exception:
        logger.exception("Could not build session insights")
        insights = {"strongest": [], "focus": [], "wrong_count": max(0, total - correct)}

    strongest = insights.get("strongest") or []
    focus = insights.get("focus") or []
    correct_skills = [x for x in strongest if int(x.get("accuracy") or 0) >= 75]
    weak_skills = [x for x in focus if int(x.get("accuracy") or 0) < 75]
    strong_line = html.escape(str(correct_skills[0]["skill"])) if correct_skills else "ще збираємо дані"
    focus_line = html.escape(str(weak_skills[0]["skill"])) if weak_skills else "явного слабкого сигналу немає"

    if session_type == "intro":
        remembered = int(insights.get("wrong_count") or 0)
        if remembered:
            memory_line = f"У повторення додано: <b>{focus_line}</b>."
        else:
            memory_line = "У цій трійці помилок не було — наступне заняття уточнить профіль."
        text = (
            f"<b>Перший профіль · {correct}/{total}</b>\n\n"
            f"Точність у цій трійці: <b>{accuracy}%</b>\n"
            f"Сильніший сигнал: <b>{strong_line}</b>\n"
            f"На повторення: <b>{focus_line}</b>\n\n"
            f"<b>Neta Memory</b>\n{memory_line}\n\n"
            "Три питання — це не оцінка рівня і не прогноз бала НМТ. Далі Neta змішуватиме нові завдання з твоїми повтореннями."
        )
        await message.answer(text, reply_markup=get_intro_result_keyboard())
        await message.answer(
            "Хочеш одне м’яке нагадування на день за київським часом? Якщо Daily уже виконано, воно не прийде.",
            reply_markup=get_reminder_offer_keyboard(),
        )
        return

    if session_type == "diagnostic":
        try:
            await LearningDB.save_diagnostic_snapshot(int(session.get("user_id")), insights)
        except Exception:
            logger.exception("Could not save diagnostic snapshot")
        strong_names = ", ".join(html.escape(str(x.get("skill"))) for x in correct_skills[:3]) or "ще немає стабільного сильного сигналу"
        weak_names = ", ".join(html.escape(str(x.get("skill"))) for x in weak_skills[:3]) or "явної слабкої навички не видно"
        text = (
            "<b>Карта навичок готова</b>\n\n"
            f"Результат вибірки: <b>{correct}/{total}</b> · {accuracy}%\n"
            f"Сильніше зараз: <b>{strong_names}</b>\n"
            f"Фокус: <b>{weak_names}</b>\n\n"
            "Це навчальна діагностика для персоналізації практики, а не офіційний рівень англійської чи прогноз бала НМТ."
        )
        await message.answer(text, reply_markup=get_diagnostic_result_keyboard())
        return

    try:
        session_xp = await LearningDB.get_session_xp(str(session.get("id")), int(session.get("user_id")))
    except Exception:
        logger.exception("Could not read session XP")
        session_xp = 0

    if session_type == "practice":
        text = (
            "<b>🧠 Тренування завершено</b>\n\n"
            f"🎯 <b>{correct}/{total} · {accuracy}%</b>\n"
            f"⭐ За сесію: <b>+{session_xp} XP</b>\n\n"
            f"✓ Сильніше: <b>{strong_line}</b>\n"
            f"↻ Повторимо: <b>{focus_line}</b>\n\n"
            "Neta Memory оновлена. Можеш зупинитися або продовжити — денного ліміту на навчання немає."
        )
        await message.answer(text, reply_markup=get_practice_result_keyboard(had_errors=correct < total))
        return

    try:
        streak = await LearningDB.get_streak(int(session.get("user_id")))
    except Exception:
        logger.exception("Could not read streak")
        streak = 0
    streak_line = f"\n🔥 Серія: <b>{streak} дн.</b>" if streak > 0 else ""
    had_errors = correct < total
    if had_errors:
        memory_line = (
            f"Ти помилився у темі <b>{focus_line}</b>. Neta додала її до повторення."
            if focus_line != "явного слабкого сигналу немає"
            else "Neta додала сьогоднішні помилки до повторення."
        )
        next_line = "Закріпимо їх зараз?"
    else:
        memory_line = "Сьогодні без помилок. Neta готова підняти складність."
        next_line = "Спробуємо складніший короткий блок?"

    text = (
        f"<b>⚡ Daily завершено — {correct}/{total} ✅</b>\n\n"
        f"{memory_line}\n\n"
        f"⭐ <b>+{session_xp} XP</b>"
        f"{streak_line}\n\n"
        f"{next_line}"
    )
    await message.answer(text, reply_markup=get_daily_result_keyboard(had_errors=had_errors))


async def _start_or_resume(message: Message, user_id: int, session_type: str, length_override: Optional[int] = None, practice_mode: str = "full") -> None:
    started = time.perf_counter()
    lengths = {"intro": 3, "daily": 4, "practice": 5, "diagnostic": 12}
    length = int(length_override) if length_override is not None else lengths.get(session_type, 4)
    try:
        session = await LearningDB.get_or_create_session(user_id, session_type, length, practice_mode=practice_mode)
        actual_type = str(session.get("session_type") or session_type)
        if session.get("status") == "completed":
            await _send_session_result(message, session)
            return
        if actual_type != session_type:
            await message.answer("Спочатку продовжимо незавершене заняття — прогрес уже збережений.")
            await _send_current_question(message, session, intro=actual_type == "intro")
            return
        await _send_current_question(message, session, intro=actual_type == "intro")
        event_map = {
            "intro": "first_lesson_started",
            "daily": "daily_lesson_started",
            "practice": "practice_started",
            "diagnostic": "diagnostic_started",
        }
        event = event_map.get(session_type, f"{session_type}_started")
        _background(LearningDB.log_event(
            user_id, event,
            {
                "session_id": str(session.get("id")),
                "length": len(session.get("question_ids") or []),
            },
            event_key=f"{event}:{session.get('id')}",
        ))
    except Exception as exc:
        logger.exception("Could not start/resume session")
        _background(LearningDB.record_error("session_start", "start_or_resume", user_id, {"error": str(exc), "session_type": session_type}))
        await message.answer("Не вдалося відкрити заняття. Спробуй ще раз — прогрес не буде втрачено.", reply_markup=get_back_keyboard())
    finally:
        elapsed = round((time.perf_counter() - started) * 1000)
        _background(LearningDB.record_metric("lesson_start_ms", elapsed, user_id, {"session_type": session_type}))


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    if not message.from_user:
        return
    user = message.from_user
    args = message.text.split(maxsplit=1)[1].strip() if message.text and " " in message.text else ""
    referrer_id: Optional[int] = None
    if args.startswith("ref_") and args[4:].isdigit():
        candidate = int(args[4:])
        if candidate != user.id:
            referrer_id = candidate
    source = "referral" if referrer_id else (args or "direct")

    t0 = time.perf_counter()
    row: Dict[str, Any] = {}
    active: Optional[Dict[str, Any]] = None
    intro_done = False
    try:
        context = await LearningDB.start_context(
            user.id, user.username, user.first_name, source, referrer_id
        )
        row = context.get("user") or {}
        active = context.get("session")
        intro_done = bool(context.get("intro_done"))
        _background(LearningDB.log_event(user.id, "bot_started", {"start_param": source}))
        if referrer_id and int(row.get("referrer_id") or 0) == referrer_id:
            _background(LearningDB.log_event(
                user.id, "referral_visit", {"referrer_id": referrer_id},
                event_key=f"referral_visit:{user.id}",
            ))
    except Exception as exc:
        logger.exception("/start failed")
        _background(LearningDB.record_error("start", "cmd_start", user.id, {"error": str(exc)}))
        await message.answer("Бот тимчасово не може під’єднатися до бази. Спробуй /start ще раз трохи пізніше.")
        return
    finally:
        _background(LearningDB.record_metric("start_handler_ms", round((time.perf_counter() - t0) * 1000), user.id))

    if active and active.get("status") == "active":
        names = {"intro": "першу сесію", "daily": "сьогоднішнє заняття", "practice": "додаткове тренування", "diagnostic": "карту навичок"}
        label = names.get(str(active.get("session_type")), "заняття")
        await message.answer(f"У тебе є незавершене {label}. Продовжуємо з того самого питання.")
        await _send_current_question(message, active, intro=active.get("session_type") == "intro")
        return

    if not intro_done:
        await message.answer(
            f"Привіт, <b>{html.escape(user.first_name or 'учню')}</b>.\n\n"
            "<b>Neta — 5 хвилин англійської, які підлаштовуються під тебе.</b>\n\n"
            "• запам’ятовує помилки\n"
            "• повертає потрібне в повторення\n"
            "• показує сильні навички й фокус\n\n"
            "Спробуй 3 питання — і одразу побачиш, як працює твій перший Neta Memory-профіль. Без обов’язкової довгої діагностики.",
            reply_markup=get_start_keyboard(),
        )
        _background(LearningDB.log_event(user.id, "value_proposition_shown", event_key=f"value_proposition_shown:{user.id}"))
        return
    await _main_screen(message, user.id)


@router.callback_query(F.data == "start_intro")
async def start_intro(callback: CallbackQuery):
    await callback.answer()
    await _start_or_resume(callback.message, callback.from_user.id, "intro")


@router.callback_query(F.data.in_({"start_today", "start_daily"}))
async def start_today(callback: CallbackQuery):
    await callback.answer()
    await _start_or_resume(callback.message, callback.from_user.id, "daily")


@router.callback_query(F.data == "show_practice")
async def show_practice(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>🧠 Тренування</b>\n\n"
        "Можеш точково попрацювати над слабкими темами або пройти повний змішаний блок. "
        "Neta Memory сама підбере завдання під твою історію.\n\n"
        "⭐ За навчання отримуєш XP; денного ліміту на тренування немає.",
        reply_markup=get_practice_picker_keyboard(),
    )


@router.callback_query(F.data.startswith("start_practice:"))
async def start_practice(callback: CallbackQuery):
    await callback.answer()
    parts = str(callback.data).split(":")
    mode = "full"
    length = 5
    try:
        if len(parts) >= 3:
            mode = parts[1] if parts[1] in {"focus", "challenge", "full"} else "full"
            length = int(parts[2])
        else:  # backwards compatibility with unpublished v6 buttons
            length = int(parts[1])
            mode = "full"
    except Exception:
        mode, length = "full", 5
    length = 10 if length >= 10 else 5
    await _start_or_resume(
        callback.message,
        callback.from_user.id,
        "practice",
        length_override=length,
        practice_mode=mode,
    )


@router.callback_query(F.data == "start_diagnostic")
async def start_diagnostic(callback: CallbackQuery):
    await callback.answer()
    await _start_or_resume(callback.message, callback.from_user.id, "diagnostic")


@router.callback_query(F.data.startswith("learn_answer:"))
async def answer_question(callback: CallbackQuery):
    await callback.answer()  # Telegram acknowledgement first; DB work follows.
    user_id = callback.from_user.id
    try:
        _, session_id, raw_index, raw_selected = str(callback.data).split(":", 3)
        question_index = int(raw_index)
        selected = int(raw_selected)
        if selected not in range(4) or question_index < 0:
            raise ValueError("invalid callback indices")
    except Exception:
        return

    started = time.perf_counter()
    try:
        session = await LearningDB.get_session(session_id, user_id)
        if not session:
            await callback.message.answer("Це заняття вже недоступне. Відкрий «Заняття на сьогодні».", reply_markup=get_back_keyboard())
            return
        session_type = str(session.get("session_type") or "daily")
        ids = [str(x) for x in (session.get("question_ids") or [])]
        if question_index >= len(ids):
            return
        questions = await LearningDB.get_questions(ids)
        question = questions[question_index]
        if str(question.get("id")) != ids[question_index]:
            raise RuntimeError("question order mismatch")
        correct_index = _correct_index(question)
        is_correct = selected == correct_index

        result = await LearningDB.record_answer(session_id, user_id, ids[question_index], question_index, selected, is_correct)
        if not result.get("inserted"):
            return
        is_correct = bool(result.get("is_correct", is_correct))

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        if session_type == "diagnostic":
            feedback = "Відповідь збережено."
        else:
            explanation = html.escape(str(question.get("explanation") or "Коротке пояснення для цього питання ще не додано."))
            skill = html.escape(skill_name(question))
            if is_correct:
                feedback = f"✓ <b>Правильно · {skill}</b>\n{explanation}"
            else:
                feedback = (
                    f"↻ <b>На повторення · {skill}</b>\n"
                    f"Правильна відповідь: <b>{LETTERS[correct_index]}</b>\n"
                    f"{explanation}\n\n"
                    "<i>Neta Memory додала цю навичку в повторення.</i>"
                )

        _background(LearningDB.log_event(
            user_id,
            "question_answered",
            {"session_id": session_id, "question_index": question_index, "is_correct": is_correct, "session_type": session_type},
            event_key=f"answered:{session_id}:{question_index}",
        ))

        if result.get("status") == "completed":
            fresh = await LearningDB.get_session(session_id, user_id) or session
            event_map = {
                "intro": "first_lesson_completed",
                "daily": "daily_lesson_completed",
                "practice": "practice_completed",
                "diagnostic": "diagnostic_completed",
            }
            event = event_map.get(session_type, f"{session_type}_completed")
            _background(LearningDB.log_event(
                user_id, event,
                {"session_id": session_id, "correct": result.get("correct_count"), "total": result.get("total")},
                event_key=f"{event}:{session_id}",
            ))
            if session_type == "intro":
                referrer = await LearningDB.activate_referral_if_eligible(user_id)
                if referrer:
                    _background(LearningDB.log_event(
                        user_id, "referral_activated", {"referrer_id": referrer},
                        event_key=f"referral_activated:{user_id}",
                    ))
            if session_type != "diagnostic":
                await callback.message.answer(feedback)
            await _send_session_result(callback.message, fresh)
            return

        next_index = int(result.get("current_index") or (question_index + 1))
        fresh = await LearningDB.get_session(session_id, user_id) or session
        questions = await _load_session_questions(fresh)
        if next_index >= len(questions):
            if session_type != "diagnostic":
                await callback.message.answer(feedback)
            await _send_session_result(callback.message, fresh)
            return
        next_q = questions[next_index]
        combined = _question_text(next_q, next_index, len(questions), prefix=feedback)
        await callback.message.answer(
            combined,
            reply_markup=get_question_keyboard(session_id, next_index, _options(next_q)),
        )
        _background(LearningDB.log_event(
            user_id, "question_shown",
            {"session_id": session_id, "question_index": next_index, "session_type": session_type},
            event_key=f"shown:{session_id}:{next_index}",
        ))
    except Exception as exc:
        logger.exception("Answer persistence failed")
        _background(LearningDB.record_error("answer_save", "answer_question", user_id, {"error": str(exc), "session_id": session_id}))
        await callback.message.answer("Не вдалося надійно зберегти відповідь. Натисни відповідь ще раз — повторне зарахування захищене.")
    finally:
        _background(LearningDB.record_metric("answer_handler_ms", round((time.perf_counter() - started) * 1000), user_id, {"session_type": session_type if 'session_type' in locals() else "unknown"}))


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await _main_screen(callback.message, callback.from_user.id, edit=True)


@router.callback_query(F.data == "show_progress")
async def show_progress(callback: CallbackQuery):
    await callback.answer()
    try:
        data, has_diagnostic = await asyncio.gather(
            LearningDB.get_progress(callback.from_user.id),
            LearningDB.has_new_diagnostic(callback.from_user.id),
        )
    except Exception:
        logger.exception("Progress failed")
        await callback.message.edit_text("Прогрес тимчасово недоступний.", reply_markup=get_back_keyboard())
        return

    attempts = int(data.get("attempts") or 0)
    if not attempts:
        body = "Після першого заняття тут з’являться точність, сильні теми й те, що варто повторити."
    else:
        skills = data.get("skills") or []
        strong = [x for x in skills if int(x.get("attempts") or 0) >= 2 and int(x.get("accuracy") or 0) >= 75]
        focus = [x for x in skills if int(x.get("accuracy") or 0) < 75]
        streak = int(data.get("streak") or 0)
        day_word = "день" if streak == 1 else "дн."
        lines = [
            f"📚 Навчальних днів: <b>{int(data.get('learning_days') or 0)}</b>",
            f"🔥 Серія: <b>{streak} {day_word}</b>",
            f"🎯 Точність: <b>{int(data.get('accuracy') or 0)}%</b>",
            f"✍️ Виконано завдань: <b>{attempts}</b>",
        ]
        if strong:
            lines.append("\n<b>Сильні теми</b>")
            for item in sorted(strong, key=lambda x: (-int(x.get("accuracy") or 0), -int(x.get("attempts") or 0)))[:3]:
                lines.append(f"✅ {html.escape(str(item['skill']))} — {item['accuracy']}%")
        if focus:
            lines.append("\n<b>Варто повторити</b>")
            for item in sorted(focus, key=lambda x: (int(x.get("accuracy") or 0), -int(x.get("attempts") or 0)))[:3]:
                lines.append(f"↻ {html.escape(str(item['skill']))} — {item['accuracy']}%")
        body = "\n".join(lines)

    diagnostic_line = "" if has_diagnostic else "\n\nХочеш точнішу картину? Пройди карту навичок із 12 завдань."
    _background(LearningDB.log_event(callback.from_user.id, "progress_opened"))
    await callback.message.edit_text(
        "<b>🧠 Мій прогрес</b>\n\n" + body + diagnostic_line,
        reply_markup=get_progress_keyboard(has_new_diagnostic=has_diagnostic),
    )


@router.callback_query(F.data == "show_friends")
async def show_friends(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    info = await bot.get_me()
    _, share_url = build_referral_share_url(info.username, callback.from_user.id)
    settings = await LearningDB.get_settings(callback.from_user.id)
    opted_in = bool(settings.get("leaderboard_opt_in"))
    data = await LearningDB.leaderboard(callback.from_user.id)
    rows = data.get("rows") or []
    medals = ("🥇", "🥈", "🥉")
    ranking = "\n".join(
        f"{medals[i-1] if i <= 3 else f'{i}.'} {html.escape(str(row['alias']))} — <b>{int(row.get('xp') or 0)} XP</b>"
        for i, row in enumerate(rows, 1)
    ) or "Поки рейтинг порожній — можеш запросити першого друга."
    my_rank = data.get("my_rank")
    my_xp = int(data.get("my_xp") or 0)
    if opted_in and my_rank:
        my_line = f"\n\nТвоє місце: <b>#{my_rank}</b> · {my_xp} XP"
    elif opted_in:
        my_line = "\n\nТи вже в рейтингу — місце з’явиться після першого XP цього тижня."
    else:
        my_line = "\n\nУвійди в рейтинг, щоб бачити своє місце."

    await callback.message.edit_text(
        "<b>🏆 Рейтинг тижня</b>\n\n"
        "Заробляй XP за правильні відповіді, Daily та повторення помилок. "
        "Рейтинг оновлюється щотижня.\n\n"
        f"{ranking}{my_line}",
        reply_markup=get_friends_keyboard(share_url, opted_in),
    )


@router.callback_query(F.data.in_({"leaderboard_on", "leaderboard_off"}))
async def leaderboard_toggle(callback: CallbackQuery, bot: Bot):
    enabled = callback.data == "leaderboard_on"
    await callback.answer("Рейтинг увімкнено" if enabled else "Ти вийшов із рейтингу")
    await LearningDB.set_leaderboard_opt_in(callback.from_user.id, enabled)
    _background(LearningDB.log_event(callback.from_user.id, "leaderboard_opt_in" if enabled else "leaderboard_opt_out"))

    if not enabled:
        settings = await LearningDB.get_settings(callback.from_user.id)
        reminder_enabled = bool(settings.get("reminder_enabled"))
        current = str(settings.get("reminder_time") or "")[:5]
        body = f"Нагадування: <b>{current} за Києвом</b>." if reminder_enabled else "Нагадування вимкнені."
        await callback.message.edit_text(
            "<b>⚙️ Налаштування</b>\n\n" + body + "\nТи не береш участі в публічному рейтингу.",
            reply_markup=get_settings_keyboard(reminder_enabled, leaderboard_opt_in=False),
        )
        return

    info = await bot.get_me()
    _, share_url = build_referral_share_url(info.username, callback.from_user.id)
    data = await LearningDB.leaderboard(callback.from_user.id)
    rows = data.get("rows") or []
    medals = ("🥇", "🥈", "🥉")
    ranking = "\n".join(
        f"{medals[i-1] if i <= 3 else f'{i}.'} {html.escape(str(row['alias']))} — <b>{int(row.get('xp') or 0)} XP</b>"
        for i, row in enumerate(rows, 1)
    ) or "Поки рейтинг порожній — можеш запросити першого друга."
    my_rank = data.get("my_rank")
    my_xp = int(data.get("my_xp") or 0)
    my_line = f"\n\nТвоє місце: <b>#{my_rank}</b> · {my_xp} XP" if my_rank else "\n\nТи в рейтингу."
    await callback.message.edit_text(
        "<b>🏆 Рейтинг тижня</b>\n\n"
        "Заробляй XP за правильні відповіді, Daily та повторення помилок. "
        "Рейтинг оновлюється щотижня.\n\n"
        f"{ranking}{my_line}",
        reply_markup=get_friends_keyboard(share_url, True),
    )


@router.callback_query(F.data == "show_course")
async def show_course(callback: CallbackQuery):
    await callback.answer()
    interested, progress = await asyncio.gather(
        LearningDB.has_event(callback.from_user.id, "course_interest"),
        LearningDB.get_progress(callback.from_user.id),
    )
    _background(LearningDB.log_event(callback.from_user.id, "course_view"))
    focus = [x for x in (progress.get("skills") or []) if int(x.get("accuracy") or 0) < 75]
    if focus:
        focus.sort(key=lambda x: (int(x.get("accuracy") or 0), -int(x.get("attempts") or 0)))
        focus_line = (
            f"Твоя практика показує, що зараз варто посилити "
            f"<b>{html.escape(str(focus[0]['skill']))}</b>.\n\n"
        )
    else:
        focus_line = "Neta вже збирає твою історію практики, щоб бачити, що варто посилити далі.\n\n"

    text = (
        "<b>🎓 Neta School</b>\n\n"
        f"{focus_line}"
        "Neta проведе тебе повним маршрутом:\n"
        "<b>короткий урок → практика → повторення → контроль прогресу</b>\n\n"
        + (
            "🔔 Ти вже у списку раннього доступу. Повідомимо про програму, ціну та старт."
            if interested else
            "Залиш заявку — повідомимо про програму, ціну та старт першими."
        )
    )
    await callback.message.edit_text(text, reply_markup=get_course_keyboard(interested))


@router.callback_query(F.data == "course_interest")
async def course_interest(callback: CallbackQuery):
    await callback.answer("Додано до раннього доступу")
    _background(LearningDB.log_event(callback.from_user.id, "course_interest", event_key=f"course_interest:{callback.from_user.id}"))
    await callback.message.edit_text(
        "<b>Готово! Ти у списку раннього доступу 💙</b>\n\n"
        "Напишемо, коли відкриється програма.",
        reply_markup=get_course_keyboard(True),
    )


@router.callback_query(F.data == "show_channel")
async def show_channel(callback: CallbackQuery):
    await callback.answer()
    _background(LearningDB.log_event(callback.from_user.id, "channel_view"))
    await callback.message.edit_text(
        "<b>Канал Neta · розбори НМТ</b>\n\n"
        "У боті — персональна практика. У каналі — короткі розбори пасток НМТ, лексика, граматика й корисні матеріали між заняттями.\n\n"
        "Підписка добровільна: Neta Memory і Daily працюють незалежно від каналу.",
        reply_markup=get_channel_keyboard(CHANNEL_URL),
    )


@router.callback_query(F.data == "show_settings")
async def show_settings(callback: CallbackQuery):
    await callback.answer()
    settings = await LearningDB.get_settings(callback.from_user.id)
    enabled = bool(settings.get("reminder_enabled"))
    leaderboard_opt_in = bool(settings.get("leaderboard_opt_in"))
    current = str(settings.get("reminder_time") or "")[:5]
    body = f"Нагадування: <b>{current} за Києвом</b>." if enabled else "Нагадування вимкнені."
    ranking_line = "\nРейтинг: <b>увімкнено</b>." if leaderboard_opt_in else "\nРейтинг: <b>не беру участі</b>."
    await callback.message.edit_text(
        "<b>⚙️ Налаштування</b>\n\n" + body + ranking_line,
        reply_markup=get_settings_keyboard(enabled, leaderboard_opt_in=leaderboard_opt_in),
    )


@router.callback_query(F.data == "show_privacy")
async def show_privacy(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>Приватність у Neta</b>\n\n"
        "Для роботи бот зберігає Telegram ID, доступні ім’я/username, відповіді, навчальний прогрес і налаштування нагадувань.\n\n"
        "У публічному тижневому рейтингу показується лише згенерований псевдонім. Neta не просить школу, місто чи номер телефону для навчання.\n\n"
        "Нагадування добровільні й вимикаються в один клік.",
        reply_markup=get_privacy_keyboard(),
    )


@router.callback_query(F.data.startswith("reminder_set:"))
async def set_reminder(callback: CallbackQuery):
    await callback.answer("Нагадування збережено")
    value = str(callback.data).split(":", 1)[1]
    if value not in {"17:00", "19:00", "21:00"}:
        return
    await LearningDB.set_reminder(callback.from_user.id, True, value)
    _background(LearningDB.log_event(callback.from_user.id, "reminder_enabled", {"time": value}))
    await callback.message.edit_text(
        f"Нагадування увімкнено на <b>{value}</b> за Києвом. Якщо заняття вже виконано, повідомлення цього дня не прийде.",
        reply_markup=get_back_keyboard(),
    )


@router.callback_query(F.data == "reminder_off")
async def reminder_off(callback: CallbackQuery):
    await callback.answer("Нагадування вимкнено")
    await LearningDB.set_reminder(callback.from_user.id, False)
    _background(LearningDB.log_event(callback.from_user.id, "reminder_disabled"))
    await callback.message.edit_text("Нагадування вимкнено.", reply_markup=get_back_keyboard())


@router.callback_query(F.data == "reminder_skip")
async def reminder_skip(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Добре. Нагадування можна ввімкнути пізніше в налаштуваннях.", reply_markup=get_back_keyboard())


# Existing invoices are no longer promoted in the UI, but checkout/payment
# callbacks remain so already-started Telegram Stars payments can complete safely.
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    expected = {"premium_3days": PREMIUM_3_DAYS_PRICE, "premium_30days": PREMIUM_30_DAYS_PRICE}
    amount = expected.get(pre_checkout_query.invoice_payload)
    if amount is None or pre_checkout_query.total_amount != amount:
        await pre_checkout_query.answer(ok=False, error_message="Платіж не відповідає тарифу.")
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment = message.successful_payment
    if not payment or not message.from_user:
        return
    days_map = {"premium_3days": PREMIUM_3_DAYS, "premium_30days": PREMIUM_30_DAYS}
    price_map = {"premium_3days": PREMIUM_3_DAYS_PRICE, "premium_30days": PREMIUM_30_DAYS_PRICE}
    days = days_map.get(payment.invoice_payload)
    if not days or payment.total_amount != price_map.get(payment.invoice_payload):
        return
    try:
        user = await DBClient.grant_premium(message.from_user.id, days)
        # Preserve a durable payment history for old/in-flight Premium purchases.
        charge_id = str(payment.telegram_payment_charge_id or "")
        order_id = f"tg_{charge_id}" if charge_id else f"tg_{message.from_user.id}_{int(datetime.now().timestamp())}"
        def _save_order():
            from bot.db_client import supabase
            supabase.table("orders").upsert({
                "order_id": order_id,
                "user_id": message.from_user.id,
                "amount": payment.total_amount,
                "status": "paid",
                "currency": payment.currency,
                "premium_days": days,
                "payment_provider": "telegram_stars",
                "telegram_payment_charge_id": charge_id or None,
                "telegram_provider_payment_charge_id": str(payment.provider_payment_charge_id or "") or None,
                "payload": payment.invoice_payload,
                "updated_at": datetime.now().astimezone().isoformat(),
            }).execute()
        await DBClient._run_sync(_save_order)
        await message.answer(f"Платіж отримано. Уже оплачене право збережено до <code>{str(user.get('premium_until') or '')[:10]}</code>.")
    except Exception as exc:
        logger.exception("Legacy payment activation failed")
        _background(LearningDB.record_error("payment", "successful_payment", message.from_user.id, {"error": str(exc)}))
        await message.answer("Платіж отримано, але активацію не вдалося завершити автоматично. Звернися до адміністратора.")


async def daily_retention_loop(bot: Bot):
    while True:
        try:
            now = datetime.now(KYIV).replace(second=0, microsecond=0)
            candidates = await LearningDB.reminder_candidates(now)
            for user_id in candidates:
                try:
                    await bot.send_message(
                        user_id,
                        "Нагадування про коротке заняття з англійської. Якщо сьогодні зручно — воно вже готове.",
                        reply_markup=get_main_keyboard(daily_completed=False, is_admin=user_id in ADMIN_IDS),
                    )
                    await LearningDB.mark_reminder_sent(user_id)
                    _background(LearningDB.log_event(user_id, "reminder_sent", {"time": now.strftime("%H:%M")}))
                except TelegramForbiddenError:
                    await LearningDB.set_user_inactive(user_id)
                except Exception as exc:
                    logger.exception("Reminder failed for %s", user_id)
                    _background(LearningDB.record_error("reminder", "daily_retention_loop", user_id, {"error": str(exc)}))
        except Exception:
            logger.exception("Reminder loop failed")
        await asyncio.sleep(60)
