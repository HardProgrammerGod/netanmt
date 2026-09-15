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
    get_progress_keyboard,
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
    task = html.escape(str(question.get("nmt_task_type") or "").strip())
    head = f"<b>{index + 1}/{total} · {skill}</b>"
    if task:
        head += f" · {task}"
    body = html.escape(str(question.get("question_text") or ""))
    if prefix:
        return f"{prefix}\n\n{head}\n\n{body}"
    return f"{head}\n\n{body}"


async def _main_screen(message: Message, user_id: int, edit: bool = False) -> None:
    try:
        done = await LearningDB.is_today_completed(user_id)
    except Exception:
        logger.exception("Could not read daily status")
        done = False
    text = (
        "<b>NMT English</b>\n\n"
        + ("Сьогоднішнє заняття вже виконано. Можеш подивитися прогрес або повернутися завтра."
           if done else "Коротке заняття на сьогодні: 3–5 питань із повторенням помилок і новою практикою.")
    )
    markup = get_main_keyboard(daily_completed=done, is_admin=user_id in ADMIN_IDS)
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
    strong_line = html.escape(str(correct_skills[0]["skill"])) if correct_skills else "поки замало даних"
    focus_line = html.escape(str(weak_skills[0]["skill"])) if weak_skills else "наступні заняття уточнять"

    if session_type == "intro":
        remembered = int(insights.get("wrong_count") or 0)
        suffix = "у" if remembered == 1 else "и" if remembered in (2, 3, 4) else "ок"
        memory_line = (
            f"Neta зберегла <b>{remembered}</b> помилк{suffix} для майбутнього повторення."
            if remembered else
            "Помилок у цій трійці не було — наступні заняття дадуть більше даних для персоналізації."
        )
        text = (
            "<b>Перший профіль готовий</b>\n\n"
            f"Результат: <b>{correct}/{total}</b> · {accuracy}%\n"
            f"Сильніший сигнал: <b>{strong_line}</b>\n"
            f"На повторення: <b>{focus_line}</b>\n\n"
            f"<b>Neta Memory:</b> {memory_line}\n\n"
            "Це лише 3 питання, тому це не оцінка рівня англійської і не прогноз бала НМТ. Перше повне заняття вже використає ці відповіді."
        )
        await message.answer(text, reply_markup=get_intro_result_keyboard())
        await message.answer(
            "Хочеш м’яке нагадування за київським часом? Якщо заняття вже виконано, цього дня воно не прийде.",
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
            f"Відповіді: <b>{correct}/{total}</b> · {accuracy}% у цій вибірці.\n"
            f"Сильніше зараз: <b>{strong_names}</b>.\n"
            f"Фокус: <b>{weak_names}</b>.\n\n"
            "Це навчальна діагностика для вибору практики, а не достовірний рівень англійської чи прогноз бала НМТ."
        )
        await message.answer(text, reply_markup=get_diagnostic_result_keyboard())
        return

    text = (
        f"<b>Заняття завершено: {correct}/{total}</b>\n\n"
        f"Точність сьогодні — <b>{accuracy}%</b>.\n"
        f"Сильніше: <b>{strong_line}</b>.\n"
        f"Фокус наступних повторень: <b>{focus_line}</b>.\n\n"
        "<b>Neta Memory оновлено.</b> Помилки повернуться у наступну практику, а нові питання допоможуть уточнювати карту навичок."
    )
    await message.answer(text, reply_markup=get_daily_result_keyboard())


async def _start_or_resume(message: Message, user_id: int, session_type: str) -> None:
    started = time.perf_counter()
    lengths = {"intro": 3, "daily": 4, "diagnostic": 12}
    length = lengths.get(session_type, 4)
    try:
        session = await LearningDB.get_or_create_session(user_id, session_type, length)
        if session.get("status") == "completed":
            await _send_session_result(message, session)
            return
        await _send_current_question(message, session, intro=session_type == "intro")
        event_map = {
            "intro": "first_lesson_started",
            "daily": "daily_lesson_started",
            "diagnostic": "diagnostic_started",
        }
        event = event_map.get(session_type, f"{session_type}_started")
        _background(LearningDB.log_event(
            user_id, event,
            {"session_id": str(session.get("id"))},
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
        names = {"intro": "першу сесію", "daily": "сьогоднішнє заняття", "diagnostic": "карту навичок"}
        label = names.get(str(active.get("session_type")), "заняття")
        await message.answer(f"У тебе є незавершене {label}. Продовжуємо з того самого питання.")
        await _send_current_question(message, active, intro=active.get("session_type") == "intro")
        return

    if not intro_done:
        await message.answer(
            f"Привіт, <b>{html.escape(user.first_name or 'учню')}</b>.\n\n"
            "<b>Neta — не просто збірник тестів.</b>\n"
            "5 хвилин на день: бот запам’ятовує твої помилки, повертає їх у наступні заняття й показує конкретні навички, які вже сильніші або потребують повторення.\n\n"
            "Почни з 3 питань. Після них одразу побачиш перші сигнали свого профілю — без довгої обов’язкової діагностики.",
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
                feedback = f"<b>Правильно.</b> · {skill}\n{explanation}"
            else:
                feedback = (
                    f"<b>Правильна відповідь: {LETTERS[correct_index]}.</b> · {skill}\n"
                    f"{explanation}\n\n"
                    "Neta запам’ятала цю помилку й зможе повернути схоже завдання в наступних заняттях."
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
        body = (
            "Поки немає навчальних відповідей. Після першої сесії тут з’являться конкретні навички, точність і фокус наступного повторення."
        )
    else:
        skills = data.get("skills") or []
        strong = [x for x in skills if int(x.get("attempts") or 0) >= 2 and int(x.get("accuracy") or 0) >= 75]
        focus = [x for x in skills if int(x.get("accuracy") or 0) < 75]
        lines = [
            f"Навчальних днів: <b>{int(data.get('learning_days') or 0)}</b>",
            f"Відповідей: <b>{attempts}</b> · точність <b>{int(data.get('accuracy') or 0)}%</b>",
        ]
        if strong:
            lines.append("\n<b>Сильніше</b>")
            for item in sorted(strong, key=lambda x: (-int(x.get("accuracy") or 0), -int(x.get("attempts") or 0)))[:3]:
                lines.append(f"• {html.escape(str(item['skill']))}: {item['accuracy']}% · {item['attempts']} відп.")
        if focus:
            lines.append("\n<b>На повторення</b>")
            for item in sorted(focus, key=lambda x: (int(x.get("accuracy") or 0), -int(x.get("attempts") or 0)))[:3]:
                lines.append(f"• {html.escape(str(item['skill']))}: {item['accuracy']}% · {item['attempts']} відп.")
        if not strong and not focus and skills:
            lines.append("\n<b>Перші сигнали</b>")
            for item in skills[:3]:
                lines.append(f"• {html.escape(str(item['skill']))}: {item['accuracy']}% · {item['attempts']} відп.")
        body = "\n".join(lines)

    diagnostic_line = (
        "\n\nКарта навичок уже пройдена. Вона не є прогнозом бала НМТ."
        if has_diagnostic else
        "\n\nХочеш ширшу картину? Добровільна карта навичок — 12 питань (~7 хв), без прогнозу бала."
    )
    _background(LearningDB.log_event(callback.from_user.id, "progress_opened"))
    await callback.message.edit_text(
        "<b>Мій прогрес · Neta Memory</b>\n\n" + body + diagnostic_line,
        reply_markup=get_progress_keyboard(has_new_diagnostic=has_diagnostic),
    )


@router.callback_query(F.data == "show_friends")
async def show_friends(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    info = await bot.get_me()
    ref_link, share_url = build_referral_share_url(info.username, callback.from_user.id)
    settings = await LearningDB.get_settings(callback.from_user.id)
    opted_in = bool(settings.get("leaderboard_opt_in"))
    data = await LearningDB.leaderboard(callback.from_user.id)
    rows = data.get("rows") or []
    ranking = "\n".join(f"{i}. {html.escape(str(row['alias']))} — <b>{row['days']} дн.</b>" for i, row in enumerate(rows, 1)) or "Рейтинг поки порожній."
    my_rank = data.get("my_rank")
    my_line = f"\n\nТвоє місце: <b>#{my_rank}</b>" if my_rank else ""
    await callback.message.edit_text(
        "<b>З друзями</b>\n\n"
        "Тижневий рейтинг рахує лише дні, коли було завершене заняття. Максимум — 1 бал за день.\n\n"
        f"{ranking}{my_line}\n\n"
        f"Твоє посилання:\n<code>{html.escape(ref_link)}</code>",
        reply_markup=get_friends_keyboard(share_url, opted_in),
    )


@router.callback_query(F.data.in_({"leaderboard_on", "leaderboard_off"}))
async def leaderboard_toggle(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    enabled = callback.data == "leaderboard_on"
    await LearningDB.set_leaderboard_opt_in(callback.from_user.id, enabled)
    _background(LearningDB.log_event(callback.from_user.id, "leaderboard_opt_in" if enabled else "leaderboard_opt_out"))
    info = await bot.get_me()
    ref_link, share_url = build_referral_share_url(info.username, callback.from_user.id)
    data = await LearningDB.leaderboard(callback.from_user.id)
    rows = data.get("rows") or []
    ranking = "\n".join(f"{i}. {html.escape(str(row['alias']))} — <b>{row['days']} дн.</b>" for i, row in enumerate(rows, 1)) or "Рейтинг поки порожній."
    state = "Ти береш участь у рейтингу." if enabled else "Ти не береш участі у рейтингу."
    await callback.message.edit_text(
        f"<b>З друзями</b>\n\n{state} Максимум — 1 бал за навчальний день.\n\n{ranking}\n\nТвоє посилання:\n<code>{html.escape(ref_link)}</code>",
        reply_markup=get_friends_keyboard(share_url, enabled),
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
        focus_line = f"За твоєю практикою один із поточних фокусів — <b>{html.escape(str(focus[0]['skill']))}</b>.\n\n"
    else:
        focus_line = ""
    text = (
        "<b>Про курс Neta School</b>\n\n"
        f"{focus_line}"
        "Бот відповідає за коротку щоденну практику. Курс має стати другим шаром: послідовні теми, короткі пояснення, практика після уроку та зрозумілий маршрут підготовки.\n\n"
        "Курс ще готується і зараз не продається. «Мені цікаво» — лише сигнал інтересу, без оплати, бронювання чи штучного дефіциту."
    )
    await callback.message.edit_text(text, reply_markup=get_course_keyboard(interested))


@router.callback_query(F.data == "course_interest")
async def course_interest(callback: CallbackQuery):
    await callback.answer("Дякую — інтерес враховано")
    _background(LearningDB.log_event(callback.from_user.id, "course_interest", event_key=f"course_interest:{callback.from_user.id}"))
    await callback.message.edit_text(
        "<b>Про курс</b>\n\nІнтерес враховано. Коли продукт буде готовий, рішення про запуск можна буде приймати за реальним попитом, а не штучним дефіцитом.",
        reply_markup=get_course_keyboard(True),
    )


@router.callback_query(F.data == "show_channel")
async def show_channel(callback: CallbackQuery):
    await callback.answer()
    _background(LearningDB.log_event(callback.from_user.id, "channel_view"))
    await callback.message.edit_text(
        "<b>Канал Neta NMT</b>\n\n"
        "Бот — це практика й персональне повторення. Канал — короткі розбори типових пасток НМТ, корисна лексика/граматика та оновлення продукту.\n\n"
        "Підписка добровільна: навчання в боті працює і без неї.",
        reply_markup=get_channel_keyboard(CHANNEL_URL),
    )


@router.callback_query(F.data == "show_settings")
async def show_settings(callback: CallbackQuery):
    await callback.answer()
    settings = await LearningDB.get_settings(callback.from_user.id)
    enabled = bool(settings.get("reminder_enabled"))
    current = str(settings.get("reminder_time") or "")[:5]
    body = f"Нагадування: <b>{current} за Києвом</b>." if enabled else "Нагадування вимкнені."
    await callback.message.edit_text(
        "<b>Налаштування</b>\n\n" + body + "\nЇх можна змінити або вимкнути будь-коли.",
        reply_markup=get_settings_keyboard(enabled),
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
