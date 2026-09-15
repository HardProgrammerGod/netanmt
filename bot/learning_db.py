import logging
import random
import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from bot.db_client import DBClient, supabase
from bot.config import ADMIN_IDS

logger = logging.getLogger(__name__)
KYIV = ZoneInfo("Europe/Kyiv")


def normalize_category(row: Dict[str, Any]) -> str:
    raw = str(row.get("category") or row.get("topic") or "").strip()
    lower = raw.casefold()
    if "read" in lower:
        return "Reading"
    if raw in {"Grammar", "Vocabulary"} or "grammar" in lower or "vocab" in lower:
        return "Use of English"
    if raw == "Use of English":
        return raw
    return raw or "Інше"


def skill_name(row: Dict[str, Any]) -> str:
    """Stable learner-facing skill label; raw DB taxonomy remains unchanged."""
    value = str(row.get("sub_category") or normalize_category(row) or "Загальна практика").strip()
    aliases = {
        "Grammar: Gerund / Infinitive": "Gerund & Infinitive",
        "Grammar: Gerund & Infinitive": "Gerund & Infinitive",
        "Grammar: Passive Voice": "Passive Voice",
        "Grammar: Passive & Reported Speech": "Passive & Reported Speech",
        "Reading: Gapped Text": "Gapped Text",
        "Reading: Comprehension": "Comprehension",
        "Reading: Detail": "Detail",
        "Reading: Main Idea": "Main Idea",
        "Reading: Multiple Choice": "Multiple Choice",
        "Reading: Notices": "Notices",
        "Reading: Situations": "Situations",
        "Reading: Inference": "Inference",
        "Matching: Notices": "Matching · Notices",
        "Matching: Situations": "Matching · Situations",
        "Vocabulary: Collocations": "Collocations",
        "Vocabulary: Phrasal Verbs": "Phrasal Verbs",
        "Vocabulary: Word Formation": "Word Formation",
        "Vocabulary: Context": "Vocabulary in Context",
    }
    if value in aliases:
        return aliases[value]
    for prefix in ("Grammar: ", "Vocabulary: ", "Reading: "):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value[:80]


def skill_group(row: Dict[str, Any]) -> str:
    raw = str(row.get("sub_category") or "").strip()
    if raw.startswith("Grammar:"):
        return "Grammar"
    if raw.startswith("Vocabulary:"):
        return "Vocabulary"
    if raw.startswith("Reading:") or raw.startswith("Matching:"):
        return "Reading"
    category = normalize_category(row)
    return category if category in {"Reading", "Use of English"} else "Practice"


def safe_alias(first_name: Optional[str], username: Optional[str], user_id: int) -> str:
    # Public leaderboard identity must be a pseudonym, not a Telegram name/username/ID.
    first = ("Швидкий", "Точний", "Сміливий", "Спокійний", "Розумний", "Системний")
    second = ("Лексик", "Читач", "Практик", "Навігатор", "Дослідник", "Фокус")
    digest = hashlib.sha256(f"neta-public-alias:{int(user_id)}".encode()).digest()
    return f"{first[digest[0] % len(first)]} {second[digest[1] % len(second)]}"



class LearningDB:
    @staticmethod
    async def start_context(
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        source: str,
        referrer_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        target_id = int(user_id)

        def _op():
            result = supabase.rpc("ensure_learning_start_context", {
                "p_user_id": target_id,
                "p_username": username or "",
                "p_first_name": first_name or "Учень",
                "p_referrer_id": int(referrer_id) if referrer_id is not None else None,
                "p_source": (source or "direct")[:120],
                "p_public_alias": safe_alias(first_name, username, target_id),
            }).execute()
            data = result.data or {}
            if isinstance(data, list):
                data = data[0] if data else {}
            return data if isinstance(data, dict) else {}

        return await DBClient._run_sync(_op)

    @staticmethod
    async def log_event(user_id: Optional[int], name: str, metadata: Optional[Dict[str, Any]] = None, event_key: Optional[str] = None) -> None:
        def _op():
            payload = {
                "user_id": int(user_id) if user_id is not None else None,
                "event_name": str(name)[:100],
                "metadata": metadata or {},
                "event_key": event_key,
            }
            query = supabase.table("events").insert(payload)
            try:
                query.execute()
            except Exception as exc:
                # Unique event_key makes analytics idempotent. Duplicate analytics must never block learning.
                if event_key and ("duplicate" in str(exc).lower() or "unique" in str(exc).lower()):
                    return
                raise

        await DBClient._run_sync(_op)

    @staticmethod
    async def record_metric(name: str, duration_ms: Optional[int] = None, user_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        def _op():
            supabase.table("operational_metrics").insert({
                "metric_name": str(name)[:100],
                "user_id": int(user_id) if user_id is not None else None,
                "duration_ms": int(duration_ms) if duration_ms is not None else None,
                "metadata": metadata or {},
            }).execute()
        await DBClient._run_sync(_op)

    @staticmethod
    async def record_error(error_type: str, context: str, user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None) -> None:
        def _op():
            supabase.table("error_reports").insert({
                "user_id": int(user_id) if user_id is not None else None,
                "error_type": str(error_type)[:120],
                "context": str(context)[:500],
                "details": details or {},
            }).execute()
        try:
            await DBClient._run_sync(_op)
        except Exception:
            logger.exception("Failed to persist error report")

    @staticmethod
    async def get_or_create_session(user_id: int, session_type: str, length: int) -> Dict[str, Any]:
        target_id = int(user_id)
        today = datetime.now(KYIV).date().isoformat()
        if session_type == "intro":
            session_key = "intro:v3"
        elif session_type == "diagnostic":
            session_key = "diagnostic:v3"
        else:
            session_key = f"{session_type}:{today}"
        safe_length = max(3, min(int(length), 12 if session_type == "diagnostic" else 5))

        def _op():
            existing = (
                supabase.table("learning_sessions")
                .select("*")
                .eq("user_id", target_id)
                .eq("session_key", session_key)
                .limit(1)
                .execute()
            )
            if existing.data:
                return existing.data[0]

            picked = supabase.rpc("select_learning_questions", {
                "p_user_id": target_id,
                "p_session_type": session_type,
                "p_length": safe_length,
            }).execute()
            rows = picked.data or []
            question_ids = [str(r.get("question_id")) for r in rows if isinstance(r, dict) and r.get("question_id")]
            if len(question_ids) < safe_length:
                raise RuntimeError(f"Question selector returned only {len(question_ids)}/{safe_length} questions")

            payload = {
                "user_id": target_id,
                "session_key": session_key,
                "session_type": session_type,
                "learning_date": today,
                "question_ids": question_ids[:safe_length],
                "current_index": 0,
                "answered_count": 0,
                "correct_count": 0,
                "status": "active",
            }
            try:
                inserted = supabase.table("learning_sessions").insert(payload).execute()
                if inserted.data:
                    return inserted.data[0]
            except Exception:
                # Race-safe recovery if two Telegram updates create the same session.
                again = (
                    supabase.table("learning_sessions")
                    .select("*")
                    .eq("user_id", target_id)
                    .eq("session_key", session_key)
                    .limit(1)
                    .execute()
                )
                if again.data:
                    return again.data[0]
                raise
            return payload

        return await DBClient._run_sync(_op)

    @staticmethod
    async def get_questions(question_ids: List[str]) -> List[Dict[str, Any]]:
        ids = [str(x) for x in question_ids if x]
        if not ids:
            return []

        def _op():
            result = (
                supabase.table("questions")
                .select("id,topic,difficulty,question_text,options,correct_option,explanation,category,sub_category,nmt_task_type,is_active,quality_status")
                .in_("id", ids)
                .execute()
            )
            rows = result.data or []
            order = {qid: i for i, qid in enumerate(ids)}
            rows.sort(key=lambda q: order.get(str(q.get("id")), 9999))
            return rows
        return await DBClient._run_sync(_op)

    @staticmethod
    async def record_answer(session_id: str, user_id: int, question_id: str, question_index: int, selected_index: int, is_correct: bool) -> Dict[str, Any]:
        def _op():
            result = supabase.rpc("record_learning_answer", {
                "p_session_id": str(session_id),
                "p_user_id": int(user_id),
                "p_question_id": str(question_id),
                "p_question_index": int(question_index),
                "p_selected_index": int(selected_index),
                "p_is_correct": bool(is_correct),
            }).execute()
            data = result.data
            if isinstance(data, dict):
                return data
            if isinstance(data, list) and data:
                return data[0]
            raise RuntimeError("record_learning_answer returned no data")
        return await DBClient._run_sync(_op)


    @staticmethod
    async def get_session(session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        def _op():
            result = (
                supabase.table("learning_sessions")
                .select("*")
                .eq("id", str(session_id))
                .eq("user_id", int(user_id))
                .limit(1)
                .execute()
            )
            return result.data[0] if result.data else None
        return await DBClient._run_sync(_op)

    @staticmethod
    async def get_session_insights(session_id: str, user_id: int) -> Dict[str, Any]:
        target_id = int(user_id)

        def _op():
            answers = (
                supabase.table("learning_session_answers")
                .select("question_id,question_index,is_correct")
                .eq("session_id", str(session_id))
                .eq("user_id", target_id)
                .order("question_index")
                .execute()
            ).data or []
            qids = [str(a.get("question_id")) for a in answers if a.get("question_id")]
            questions: Dict[str, Dict[str, Any]] = {}
            if qids:
                qrows = (
                    supabase.table("questions")
                    .select("id,category,topic,sub_category,nmt_task_type")
                    .in_("id", qids)
                    .execute()
                ).data or []
                questions = {str(q["id"]): q for q in qrows}

            stats: Dict[str, Dict[str, int]] = {}
            for answer in answers:
                q = questions.get(str(answer.get("question_id")), {})
                name = skill_name(q)
                item = stats.setdefault(name, {"correct": 0, "attempts": 0})
                item["attempts"] += 1
                item["correct"] += 1 if answer.get("is_correct") else 0

            skills: List[Dict[str, Any]] = []
            for name, item in stats.items():
                attempts = item["attempts"]
                skills.append({
                    "skill": name,
                    "attempts": attempts,
                    "correct": item["correct"],
                    "accuracy": round(item["correct"] / attempts * 100) if attempts else 0,
                })
            strongest = sorted(skills, key=lambda x: (-x["accuracy"], -x["attempts"], x["skill"]))
            focus = sorted(skills, key=lambda x: (x["accuracy"], -x["attempts"], x["skill"]))
            return {
                "skills": skills,
                "strongest": strongest[:3],
                "focus": focus[:3],
                "total": len(answers),
                "correct": sum(1 for a in answers if a.get("is_correct")),
                "wrong_count": sum(1 for a in answers if not a.get("is_correct")),
            }

        return await DBClient._run_sync(_op)

    @staticmethod
    async def has_new_diagnostic(user_id: int) -> bool:
        def _op():
            result = (
                supabase.table("learning_sessions")
                .select("id")
                .eq("user_id", int(user_id))
                .eq("session_key", "diagnostic:v3")
                .eq("status", "completed")
                .limit(1)
                .execute()
            )
            return bool(result.data)
        return await DBClient._run_sync(_op)

    @staticmethod
    async def save_diagnostic_snapshot(user_id: int, insights: Dict[str, Any]) -> None:
        focus = insights.get("focus") or []
        weak_topics = [
            {
                "topic": str(item.get("skill") or "Навичка")[:120],
                "correct": int(item.get("correct") or 0),
                "total": int(item.get("attempts") or 0),
                "accuracy": round((int(item.get("accuracy") or 0)) / 100, 2),
            }
            for item in focus[:5]
        ]
        payload = {
            "diagnostic_correct": int(insights.get("correct") or 0),
            "diagnostic_total": int(insights.get("total") or 0),
            "diagnostic_score_min": None,
            "diagnostic_score_max": None,
            "diagnostic_weak_topics": weak_topics,
            "diagnostic_completed_at": datetime.now(timezone.utc).isoformat(),
        }

        def _op():
            supabase.table("users").update(payload).eq("id", int(user_id)).execute()
        await DBClient._run_sync(_op)

    @staticmethod
    async def is_today_completed(user_id: int) -> bool:
        today = datetime.now(KYIV).date().isoformat()
        def _op():
            result = (
                supabase.table("learning_sessions")
                .select("id")
                .eq("user_id", int(user_id))
                .eq("session_type", "daily")
                .eq("learning_date", today)
                .eq("status", "completed")
                .limit(1)
                .execute()
            )
            return bool(result.data)
        return await DBClient._run_sync(_op)

    @staticmethod
    async def has_event(user_id: int, event_name: str) -> bool:
        def _op():
            result = (
                supabase.table("events")
                .select("id")
                .eq("user_id", int(user_id))
                .eq("event_name", str(event_name))
                .limit(1)
                .execute()
            )
            return bool(result.data)
        return await DBClient._run_sync(_op)

    @staticmethod
    async def activate_referral_if_eligible(user_id: int) -> Optional[int]:
        target_id = int(user_id)

        def _op():
            result = supabase.rpc("activate_learning_referral", {
                "p_referred_user_id": target_id,
            }).execute()
            value = result.data
            if value is None:
                return None
            if isinstance(value, list):
                value = value[0] if value else None
            if isinstance(value, dict):
                value = next(iter(value.values()), None)
            return int(value) if value is not None else None

        return await DBClient._run_sync(_op)

    @staticmethod
    async def get_progress(user_id: int) -> Dict[str, Any]:
        """Read one canonical progress snapshot built from the complete user_answers history."""
        target_id = int(user_id)

        def _op():
            result = supabase.rpc("get_user_learning_progress_v5", {"p_user_id": target_id}).execute()
            data = result.data or {}
            if isinstance(data, list):
                data = data[0] if data else {}
            if not isinstance(data, dict):
                data = {}

            skills: List[Dict[str, Any]] = []
            for row in (data.get("skills") or []):
                attempts = int(row.get("attempts") or 0)
                correct = int(row.get("correct") or 0)
                if attempts <= 0:
                    continue
                skills.append({
                    "skill": skill_name(row),
                    "group": skill_group(row),
                    "attempts": attempts,
                    "correct": correct,
                    "accuracy": round(correct / attempts * 100),
                    "mastery": round(float(row.get("mastery_score") or (correct / attempts * 100))),
                })
            skills.sort(key=lambda x: (-int(x.get("attempts") or 0), int(x.get("accuracy") or 0), str(x.get("skill"))))
            attempts = int(data.get("attempts") or 0)
            correct = int(data.get("correct") or 0)
            return {
                "attempts": attempts,
                "correct": correct,
                "accuracy": round(correct / attempts * 100) if attempts else 0,
                "learning_days": int(data.get("learning_days") or 0),
                "streak": int(data.get("streak") or 0),
                "skills": skills[:20],
            }

        return await DBClient._run_sync(_op)


    @staticmethod
    async def get_streak(user_id: int) -> int:
        def _op():
            result = (
                supabase.table("users")
                .select("streak")
                .eq("id", int(user_id))
                .limit(1)
                .execute()
            )
            return int(result.data[0].get("streak") or 0) if result.data else 0
        return await DBClient._run_sync(_op)


    @staticmethod
    async def set_reminder(user_id: int, enabled: bool, reminder_time: Optional[str] = None) -> None:
        target_id = int(user_id)
        payload: Dict[str, Any] = {"reminder_enabled": bool(enabled), "reminder_timezone": "Europe/Kyiv"}
        if reminder_time:
            payload["reminder_time"] = reminder_time
        if not enabled:
            payload["reminder_time"] = None

        def _op():
            supabase.table("users").update(payload).eq("id", target_id).execute()
        await DBClient._run_sync(_op)

    @staticmethod
    async def get_settings(user_id: int) -> Dict[str, Any]:
        def _op():
            result = supabase.table("users").select("reminder_enabled,reminder_time,public_alias,is_active,leaderboard_opt_in").eq("id", int(user_id)).limit(1).execute()
            return result.data[0] if result.data else {}
        return await DBClient._run_sync(_op)

    @staticmethod
    async def reminder_candidates(now_kyiv: datetime, limit: int = 2000) -> List[int]:
        today = now_kyiv.date().isoformat()
        hhmmss = now_kyiv.strftime("%H:%M:00")

        def _op():
            result = supabase.rpc("get_learning_reminder_candidates", {
                "p_learning_date": today,
                "p_reminder_time": hhmmss,
                "p_limit": max(1, min(int(limit), 10000)),
            }).execute()
            rows = result.data or []
            out: List[int] = []
            for row in rows:
                value = row.get("user_id") if isinstance(row, dict) else row
                if value is not None:
                    out.append(int(value))
            return out

        return await DBClient._run_sync(_op)

    @staticmethod
    async def mark_reminder_sent(user_id: int) -> None:
        def _op():
            supabase.table("users").update({"last_reminder_at": datetime.now(timezone.utc).isoformat()}).eq("id", int(user_id)).execute()
        await DBClient._run_sync(_op)

    @staticmethod
    async def set_user_inactive(user_id: int) -> None:
        def _op():
            supabase.table("users").update({"is_active": False, "reminder_enabled": False}).eq("id", int(user_id)).execute()
        await DBClient._run_sync(_op)


    @staticmethod
    async def set_leaderboard_opt_in(user_id: int, enabled: bool) -> None:
        def _op():
            supabase.table("users").update({"leaderboard_opt_in": bool(enabled)}).eq("id", int(user_id)).execute()
        await DBClient._run_sync(_op)

    @staticmethod
    async def leaderboard(user_id: int) -> Dict[str, Any]:
        today = datetime.now(KYIV).date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        def _op():
            result = supabase.rpc("get_weekly_learning_leaderboard", {
                "p_user_id": int(user_id),
                "p_week_start": monday.isoformat(),
                "p_week_end": sunday.isoformat(),
                "p_limit": 10,
            }).execute()
            data = result.data or {}
            if isinstance(data, list):
                data = data[0] if data else {}
            return data if isinstance(data, dict) else {
                "rows": [], "my_rank": None,
                "week_start": monday.isoformat(), "week_end": sunday.isoformat(),
            }

        return await DBClient._run_sync(_op)

    @staticmethod
    async def admin_learning_report() -> Dict[str, Any]:
        def _op():
            result = supabase.rpc("get_learning_admin_report", {
                "p_admin_ids": [int(x) for x in ADMIN_IDS],
                "p_days": 7,
            }).execute()
            data = result.data or {}
            if isinstance(data, list):
                data = data[0] if data else {}
            return data if isinstance(data, dict) else {}

        return await DBClient._run_sync(_op)

    @staticmethod
    async def question_bank_audit() -> Dict[str, Any]:
        def _op():
            result = supabase.rpc("get_question_bank_audit", {}).execute()
            data = result.data or {}
            if isinstance(data, list):
                data = data[0] if data else {}
            return data if isinstance(data, dict) else {}

        return await DBClient._run_sync(_op)
