import asyncio
import logging
import random
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from bot.config import (
    SUPABASE_KEY,
    SUPABASE_URL,
    FREE_DAILY_QUIZ_LIMIT,
    REFERRAL_PREMIUM_DAYS,
)


logger = logging.getLogger(__name__)


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


DB_SEMAPHORE = asyncio.Semaphore(12)


class DBClient:
    """
    Async wrapper around the synchronous Supabase client.

    Supabase Python client is synchronous, therefore all SDK
    operations are executed through asyncio.to_thread().

    Semaphore protects the free Supabase instance from a large
    number of concurrent requests.
    """

    @staticmethod
    async def _run_sync(function):
        async with DB_SEMAPHORE:
            return await asyncio.to_thread(function)

    # ========================================================
    # USERS
    # ========================================================

    @staticmethod
    async def get_or_create_user(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        referrer_id: Optional[int] = None,
    ) -> Dict[str, Any]:

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("*")
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if data:
                user = data[0]

                updates: Dict[str, Any] = {}

                if username is not None and username != user.get("username"):
                    updates["username"] = username

                if first_name is not None and first_name != user.get("first_name"):
                    updates["first_name"] = first_name

                if not user.get("is_active", True):
                    updates["is_active"] = True

                if updates:
                    update_result = (
                        supabase
                        .table("users")
                        .update(updates)
                        .eq("id", target_id)
                        .execute()
                    )

                    updated_data = update_result.data or []

                    if updated_data:
                        user = updated_data[0]

                return user

            clean_referrer = None

            if referrer_id is not None:
                referrer_id_int = int(referrer_id)

                if referrer_id_int != target_id:
                    ref_result = (
                        supabase
                        .table("users")
                        .select("id")
                        .eq("id", referrer_id_int)
                        .limit(1)
                        .execute()
                    )

                    if ref_result.data:
                        clean_referrer = referrer_id_int

            new_user = {
                "id": target_id,
                "username": username or "",
                "first_name": first_name or "Учень",
                "level": 1,
                "xp": 0,
                "energy": 5,
                "max_energy": 5,
                "is_premium": False,
                "mascot_skin": "default",
                "referrer_id": clean_referrer,
                "is_active": True,
                "streak": 0,
                "total_tasks_solved": 0,
                "referrals_count": 0,
                "referral_rewarded": False,
                "premium_until": None,
                "last_active_at": datetime.now(timezone.utc).isoformat(),
                "last_streak_date": None,
                "last_reminder_at": None,
                "daily_quiz_count": 0,
                "daily_quiz_date": str(date.today()),
                "onboarding_completed": False,
                "diagnostic_correct": 0,
                "diagnostic_total": 0,
                "diagnostic_score_min": None,
                "diagnostic_score_max": None,
                "diagnostic_weak_topics": [],
                "diagnostic_completed_at": None,
            }

            insert_result = (
                supabase
                .table("users")
                .insert(new_user)
                .execute()
            )

            inserted_data = insert_result.data or []

            if inserted_data:
                return inserted_data[0]

            return new_user

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # ONBOARDING / DIAGNOSTIC
    # ========================================================

    @staticmethod
    async def save_diagnostic_result(
        user_id: int,
        correct: int,
        total: int,
        score_min: int,
        score_max: int,
        weak_topics: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        target_id = int(user_id)

        def _db_op():
            payload = {
                "onboarding_completed": True,
                "diagnostic_correct": int(correct),
                "diagnostic_total": int(total),
                "diagnostic_score_min": int(score_min),
                "diagnostic_score_max": int(score_max),
                "diagnostic_weak_topics": weak_topics[:5],
                "diagnostic_completed_at": datetime.now(timezone.utc).isoformat(),
            }

            result = (
                supabase
                .table("users")
                .update(payload)
                .eq("id", target_id)
                .execute()
            )

            data = result.data or []

            if data:
                return data[0]

            return payload

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def is_onboarding_completed(
        user_id: int,
    ) -> bool:

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("onboarding_completed")
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []
            return bool(data and data[0].get("onboarding_completed"))

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def get_diagnostic_profile(
        user_id: int,
    ) -> Dict[str, Any]:

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .select(
                    "diagnostic_correct, diagnostic_total, diagnostic_score_min, "
                    "diagnostic_score_max, diagnostic_weak_topics, diagnostic_completed_at"
                )
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []
            return data[0] if data else {}

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # ACTIVITY / STREAK
    # ========================================================

    @staticmethod
    async def record_activity(user_id: int) -> Dict[str, Any]:
        """
        Records current user activity and updates streak.

        One activity per UTC calendar day increments streak.
        Missing one or more days resets streak to 1.
        """

        target_id = int(user_id)
        today = datetime.now(timezone.utc).date()

        def _db_op():
            result = (
                supabase
                .table("users")
                .select(
                    "id, streak, last_streak_date, last_active_at, is_active"
                )
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if not data:
                return {}

            user = data[0]

            current_streak = int(user.get("streak") or 0)

            last_streak_date_raw = user.get(
                "last_streak_date"
            )

            if last_streak_date_raw:
                try:
                    last_date = date.fromisoformat(
                        str(last_streak_date_raw)
                    )
                except ValueError:
                    last_date = None
            else:
                last_date = None

            new_streak = current_streak

            if last_date == today:
                new_streak = max(current_streak, 1)

            elif last_date == today - timedelta(days=1):
                new_streak = max(current_streak, 0) + 1

            else:
                new_streak = 1

            updates = {
                "last_active_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "last_streak_date": str(today),
                "streak": new_streak,
                "is_active": True,
            }

            update_result = (
                supabase
                .table("users")
                .update(updates)
                .eq("id", target_id)
                .execute()
            )

            updated_data = update_result.data or []

            return (
                updated_data[0]
                if updated_data
                else {
                    **user,
                    **updates,
                }
            )

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # PREMIUM
    # ========================================================

    @staticmethod
    async def grant_premium(
        user_id: int,
        days: int,
    ) -> Dict[str, Any]:

        if days <= 0:
            raise ValueError("Кількість Premium-днів має бути > 0.")

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("id, is_premium, premium_until")
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if not data:
                raise ValueError(
                    f"Користувач {target_id} не знайдений."
                )

            user = data[0]

            now = datetime.now(timezone.utc)

            existing_until = None
            raw_until = user.get("premium_until")

            if raw_until:
                try:
                    existing_until = datetime.fromisoformat(
                        str(raw_until).replace("Z", "+00:00")
                    )

                    if existing_until.tzinfo is None:
                        existing_until = existing_until.replace(
                            tzinfo=timezone.utc
                        )

                except ValueError:
                    existing_until = None

            base_date = (
                existing_until
                if existing_until and existing_until > now
                else now
            )

            new_until = base_date + timedelta(days=days)

            updates = {
                "is_premium": True,
                "premium_until": new_until.isoformat(),
            }

            update_result = (
                supabase
                .table("users")
                .update(updates)
                .eq("id", target_id)
                .execute()
            )

            updated_data = update_result.data or []

            if updated_data:
                return updated_data[0]

            return {
                **user,
                **updates,
            }

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def refresh_premium_status(
        user_id: int,
    ) -> Dict[str, Any]:

        target_id = int(user_id)
        now = datetime.now(timezone.utc)

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("*")
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if not data:
                return {}

            user = data[0]

            raw_until = user.get("premium_until")

            if not raw_until:
                return user

            try:
                premium_until = datetime.fromisoformat(
                    str(raw_until).replace("Z", "+00:00")
                )

                if premium_until.tzinfo is None:
                    premium_until = premium_until.replace(
                        tzinfo=timezone.utc
                    )

            except ValueError:
                return user

            if premium_until <= now and user.get("is_premium"):
                update_result = (
                    supabase
                    .table("users")
                    .update({"is_premium": False})
                    .eq("id", target_id)
                    .execute()
                )

                updated_data = update_result.data or []

                if updated_data:
                    return updated_data[0]

                user["is_premium"] = False

            return user

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # QUIZ LIMIT
    # ========================================================

    @staticmethod
    async def can_start_quiz(
        user_id: int,
    ) -> bool:

        target_id = int(user_id)
        today = date.today()

        def _db_op():
            result = (
                supabase
                .table("users")
                .select(
                    "is_premium, daily_quiz_count, daily_quiz_date"
                )
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if not data:
                return False

            user = data[0]

            if user.get("is_premium"):
                return True

            raw_date = user.get("daily_quiz_date")

            if raw_date != str(today):
                return True

            count = int(
                user.get("daily_quiz_count") or 0
            )

            return count < FREE_DAILY_QUIZ_LIMIT

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def consume_quiz_attempt(
        user_id: int,
    ) -> bool:

        target_id = int(user_id)
        today = date.today()

        def _db_op():
            result = (
                supabase
                .table("users")
                .select(
                    "is_premium, daily_quiz_count, daily_quiz_date"
                )
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            data = result.data or []

            if not data:
                return False

            user = data[0]

            if user.get("is_premium"):
                return True

            current_date = user.get("daily_quiz_date")
            current_count = int(
                user.get("daily_quiz_count") or 0
            )

            if current_date != str(today):
                current_count = 0

            if current_count >= FREE_DAILY_QUIZ_LIMIT:
                return False

            update_result = (
                supabase
                .table("users")
                .update(
                    {
                        "daily_quiz_date": str(today),
                        "daily_quiz_count": current_count + 1,
                    }
                )
                .eq("id", target_id)
                .execute()
            )

            return bool(update_result.data)

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # QUESTIONS
    # ========================================================

    @staticmethod
    async def add_task(
        category: str,
        sub_category: str,
        section: str,
        question_text: str,
        options: Dict[str, str],
        correct_answer: str,
        explanation: str = "",
    ) -> Dict[str, Any]:

        correct_answer = correct_answer.upper().strip()

        answer_map = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
        }

        if correct_answer not in answer_map:
            raise ValueError(
                "correct_answer має бути A, B, C або D."
            )

        if len(options) != 4:
            raise ValueError(
                "Питання повинно мати рівно 4 варіанти."
            )

        clean_options = {
            "A": str(options.get("A", "")).strip(),
            "B": str(options.get("B", "")).strip(),
            "C": str(options.get("C", "")).strip(),
            "D": str(options.get("D", "")).strip(),
        }

        if any(not value for value in clean_options.values()):
            raise ValueError(
                "Усі чотири варіанти відповідей повинні бути заповнені."
            )

        def _db_op():
            payload = {
                "topic": category,
                "difficulty": 1,
                "question_text": question_text.strip(),
                "options": clean_options,
                "correct_option": answer_map[correct_answer],
                "explanation": explanation.strip(),
                "category": category,
                "sub_category": sub_category.strip(),
                "section": section.strip() or "NMT",
            }

            result = (
                supabase
                .table("questions")
                .insert(payload)
                .execute()
            )

            data = result.data or []

            if not data:
                raise RuntimeError(
                    "Supabase не повернув створене питання."
                )

            return data[0]

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def get_personalized_tasks(
        user_id: int,
        category: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        target_id = int(user_id)
        safe_limit = max(1, min(int(limit), 20))

        def _db_op():
            question_result = (
                supabase
                .table("questions")
                .select("*")
                .eq("category", category)
                .limit(100)
                .execute()
            )

            all_questions = question_result.data or []

            if not all_questions:
                return []

            answer_result = (
                supabase
                .table("user_answers")
                .select("question_id, is_correct")
                .eq("user_id", target_id)
                .limit(1000)
                .execute()
            )

            attempts = answer_result.data or []

            wrong_ids = {
                str(item.get("question_id"))
                for item in attempts
                if not item.get("is_correct")
            }

            random.shuffle(all_questions)

            wrong_questions = [
                question
                for question in all_questions
                if str(question.get("id")) in wrong_ids
            ]

            other_questions = [
                question
                for question in all_questions
                if str(question.get("id")) not in wrong_ids
            ]

            random.shuffle(wrong_questions)
            random.shuffle(other_questions)

            result = (
                wrong_questions[:safe_limit]
                + other_questions
            )

            return result[:safe_limit]

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def get_random_question(
        category: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        def _db_op():
            query = (
                supabase
                .table("questions")
                .select("*")
            )

            if category:
                query = query.eq("category", category)

            result = (
                query
                .limit(30)
                .execute()
            )

            data = result.data or []

            if not data:
                return None

            return random.choice(data)

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # ANSWERS
    # ========================================================

    @staticmethod
    async def save_attempt(
        user_id: int,
        question_id: str,
        answer: int,
        is_correct: bool,
    ) -> None:

        target_id = int(user_id)

        def _db_op():
            answer_result = (
                supabase
                .table("user_answers")
                .insert(
                    {
                        "user_id": target_id,
                        "question_id": question_id,
                        "answer": int(answer),
                        "is_correct": bool(is_correct),
                    }
                )
                .execute()
            )

            if not answer_result.data:
                raise RuntimeError(
                    "Не вдалося зберегти відповідь користувача."
                )

            user_result = (
                supabase
                .table("users")
                .select("total_tasks_solved, xp")
                .eq("id", target_id)
                .limit(1)
                .execute()
            )

            user_data = user_result.data or []

            if not user_data:
                return

            user = user_data[0]

            current_tasks = int(
                user.get("total_tasks_solved") or 0
            )

            current_xp = int(
                user.get("xp") or 0
            )

            xp_gain = 10 if is_correct else 3

            supabase.table("users").update(
                {
                    "total_tasks_solved": current_tasks + 1,
                    "xp": current_xp + xp_gain,
                }
            ).eq(
                "id",
                target_id,
            ).execute()

        await DBClient._run_sync(_db_op)

    # ========================================================
    # REFERRALS
    # ========================================================

    @staticmethod
    async def process_referral(
        new_user_id: int,
        referrer_id: Optional[int],
    ) -> bool:

        if not referrer_id:
            return False

        new_id = int(new_user_id)
        ref_id = int(referrer_id)

        if new_id == ref_id:
            return False

        def _db_op():
            new_result = (
                supabase
                .table("users")
                .select(
                    "id, referrer_id, referral_rewarded"
                )
                .eq("id", new_id)
                .limit(1)
                .execute()
            )

            new_data = new_result.data or []

            if not new_data:
                return False

            new_user = new_data[0]

            if new_user.get("referrer_id") != ref_id:
                return False

            if new_user.get("referral_rewarded"):
                return False

            referrer_result = (
                supabase
                .table("users")
                .select(
                    "id, referrals_count, is_premium, premium_until"
                )
                .eq("id", ref_id)
                .limit(1)
                .execute()
            )

            referrer_data = referrer_result.data or []

            if not referrer_data:
                return False

            referrer = referrer_data[0]

            now = datetime.now(timezone.utc)

            existing_until = None
            raw_until = referrer.get("premium_until")

            if raw_until:
                try:
                    existing_until = datetime.fromisoformat(
                        str(raw_until).replace("Z", "+00:00")
                    )

                    if existing_until.tzinfo is None:
                        existing_until = existing_until.replace(
                            tzinfo=timezone.utc
                        )

                except ValueError:
                    existing_until = None

            base_date = (
                existing_until
                if existing_until and existing_until > now
                else now
            )

            new_premium_until = (
                base_date
                + timedelta(days=REFERRAL_PREMIUM_DAYS)
            )

            new_referral_count = int(
                referrer.get("referrals_count") or 0
            ) + 1

            update_referrer = (
                supabase
                .table("users")
                .update(
                    {
                        "referrals_count": new_referral_count,
                        "is_premium": True,
                        "premium_until": new_premium_until.isoformat(),
                    }
                )
                .eq("id", ref_id)
                .execute()
            )

            if not update_referrer.data:
                return False

            update_new_user = (
                supabase
                .table("users")
                .update(
                    {
                        "referral_rewarded": True,
                    }
                )
                .eq("id", new_id)
                .execute()
            )

            return bool(update_new_user.data)

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # ADMIN
    # ========================================================

    @staticmethod
    async def get_all_user_ids() -> List[int]:

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("id")
                .eq("is_active", True)
                .limit(10000)
                .execute()
            )

            data = result.data or []

            return [
                int(item["id"])
                for item in data
                if item.get("id") is not None
            ]

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def set_user_active_status(
        user_id: int,
        is_active: bool,
    ) -> None:

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .update(
                    {
                        "is_active": bool(is_active)
                    }
                )
                .eq("id", target_id)
                .execute()
            )

            if not result.data:
                logger.warning(
                    "Не вдалося оновити active status для %s",
                    target_id,
                )

        await DBClient._run_sync(_db_op)

    @staticmethod
    async def get_admin_stats() -> Dict[str, int]:

        def _db_op():
            users_result = (
                supabase
                .table("users")
                .select(
                    "id, is_active, is_premium, premium_until, referrals_count"
                )
                .limit(10000)
                .execute()
            )

            questions_result = (
                supabase
                .table("questions")
                .select("id")
                .limit(10000)
                .execute()
            )

            users = users_result.data or []
            questions = questions_result.data or []

            now = datetime.now(timezone.utc)

            premium_users = 0

            for user in users:
                if not user.get("is_premium"):
                    continue

                raw_until = user.get("premium_until")

                if not raw_until:
                    premium_users += 1
                    continue

                try:
                    until = datetime.fromisoformat(
                        str(raw_until).replace("Z", "+00:00")
                    )

                    if until.tzinfo is None:
                        until = until.replace(
                            tzinfo=timezone.utc
                        )

                    if until > now:
                        premium_users += 1

                except ValueError:
                    premium_users += 1

            active_users = sum(
                1
                for user in users
                if user.get("is_active", True)
            )

            blocked_users = len(users) - active_users

            referrals = sum(
                int(user.get("referrals_count") or 0)
                for user in users
            )

            return {
                "total_users": len(users),
                "active_users": active_users,
                "blocked_users": blocked_users,
                "premium_users": premium_users,
                "total_questions": len(questions),
                "total_referrals": referrals,
            }

        return await DBClient._run_sync(_db_op)

    # ========================================================
    # DAILY RETENTION
    # ========================================================

    @staticmethod
    async def get_daily_reminder_candidates(
        hours: int = 24,
        limit: int = 100,
    ) -> List[int]:

        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(hours=hours)
        )

        def _db_op():
            result = (
                supabase
                .table("users")
                .select("id")
                .eq("is_active", True)
                .lt(
                    "last_active_at",
                    cutoff.isoformat(),
                )
                .limit(limit)
                .execute()
            )

            data = result.data or []

            return [
                int(item["id"])
                for item in data
                if item.get("id") is not None
            ]

        return await DBClient._run_sync(_db_op)

    @staticmethod
    async def mark_reminder_sent(
        user_id: int,
    ) -> None:

        target_id = int(user_id)

        def _db_op():
            result = (
                supabase
                .table("users")
                .update(
                    {
                        "last_reminder_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }
                )
                .eq("id", target_id)
                .execute()
            )

            if not result.data:
                logger.warning(
                    "Не вдалося записати reminder для %s",
                    target_id,
                )

        await DBClient._run_sync(_db_op)


# Compatibility instance
db_client = DBClient()
