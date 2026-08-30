import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, TypeVar

from supabase import Client, create_client

from bot.config import (
    DB_SEMAPHORE_LIMIT,
    FREE_DAILY_TESTS,
    SUPABASE_KEY,
    SUPABASE_URL,
)


logger = logging.getLogger(__name__)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

DB_SEMAPHORE = asyncio.Semaphore(DB_SEMAPHORE_LIMIT)

T = TypeVar("T")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None

    if isinstance(value, datetime):
        result = value
    else:
        try:
            result = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
        except ValueError:
            return None

    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)

    return result.astimezone(timezone.utc)


async def _run_db(operation: Callable[[], T]) -> T:
    """
    Виконує синхронний Supabase SDK у thread pool.

    Semaphore обмежує кількість одночасних операцій,
    щоб не створювати надмірне навантаження на Supabase.
    """
    async with DB_SEMAPHORE:
        return await asyncio.to_thread(operation)


class DBClient:
    """Асинхронна обгортка над синхронним Supabase SDK."""

    @staticmethod
    async def get_or_create_user(
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        referrer_id: Optional[int] = None,
        tg_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Універсальний метод отримання/створення користувача.

        tg_id залишений як compatibility alias для старого коду.
        """

        target_id = user_id if user_id is not None else tg_id

        if target_id is None:
            raise ValueError("user_id не переданий.")

        target_id = int(target_id)
        now = utc_now()
        today = now.date()

        def _db_op() -> Dict[str, Any]:
            result = (
                supabase
                .table("users")
                .select("*")
                .eq("user_id", target_id)
                .limit(1)
                .execute()
            )

            user = result.data[0] if result.data else None

            if user is None:
                new_user = {
                    "user_id": target_id,
                    "username": username or "",
                    "first_name": first_name or "Учень",
                    "daily_tests_left": FREE_DAILY_TESTS,
                    "last_test_date": today.isoformat(),
                    "is_premium": False,
                    "premium_until": None,
                    "is_active": True,
                    "total_tests_passed": 0,
                    "total_tasks_solved": 0,
                    "streak": 1,
                    "last_active_date": today.isoformat(),
                    "last_active_at": now.isoformat(),
                    "referrer_id": (
                        int(referrer_id)
                        if referrer_id and int(referrer_id) != target_id
                        else None
                    ),
                    "referral_rewarded": False,
                    "referrals_count": 0,
                    "last_reminder_at": None,
                }

                try:
                    insert_result = (
                        supabase
                        .table("users")
                        .insert(new_user)
                        .execute()
                    )

                    if insert_result.data:
                        created = insert_result.data[0]
                    else:
                        created = new_user

                    created["_is_new"] = True
                    return created

                except Exception:
                    # Можливий race condition при двох /start одночасно.
                    retry = (
                        supabase
                        .table("users")
                        .select("*")
                        .eq("user_id", target_id)
                        .limit(1)
                        .execute()
                    )

                    if retry.data:
                        user = retry.data[0]
                    else:
                        raise

            updates: Dict[str, Any] = {}

            existing_username = user.get("username")
            existing_first_name = user.get("first_name")

            if username and username != existing_username:
                updates["username"] = username

            if first_name and first_name != existing_first_name:
                updates["first_name"] = first_name

            if not user.get("is_active", True):
                updates["is_active"] = True

            last_active_date_raw = user.get("last_active_date")

            try:
                last_active_date = (
                    datetime.fromisoformat(
                        str(last_active_date_raw)
                    ).date()
                    if last_active_date_raw
                    else None
                )
            except ValueError:
                last_active_date = None

            if last_active_date != today:
                if last_active_date == today - timedelta(days=1):
                    new_streak = int(user.get("streak") or 0) + 1
                else:
                    new_streak = 1

                updates["streak"] = new_streak
                updates["last_active_date"] = today.isoformat()

            updates["last_active_at"] = now.isoformat()

            premium_until = parse_datetime(user.get("premium_until"))

            if (
                user.get("is_premium")
                and premium_until
                and premium_until <= now
            ):
                updates["is_premium"] = False

            last_test_date = user.get("last_test_date")

            if last_test_date != today.isoformat():
                updates["daily_tests_left"] = FREE_DAILY_TESTS
                updates["last_test_date"] = today.isoformat()

            if updates:
                update_result = (
                    supabase
                    .table("users")
                    .update(updates)
                    .eq("user_id", target_id)
                    .execute()
                )

                if update_result.data:
                    user = update_result.data[0]
                else:
                    user.update(updates)

            user["_is_new"] = False

            return user

        return await _run_db(_db_op)

    @staticmethod
    async def grant_premium(
        user_id: int,
        days: int,
    ) -> Optional[datetime]:
        """Додає Premium на вказану кількість днів."""

        if days <= 0:
            raise ValueError("Кількість днів Premium повинна бути > 0.")

        user_id = int(user_id)
        now = utc_now()

        def _db_op() -> Optional[datetime]:
            result = (
                supabase
                .table("users")
                .select("premium_until")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            current_until = None

            if result.data:
                current_until = parse_datetime(
                    result.data[0].get("premium_until")
                )

            base = (
                current_until
                if current_until and current_until > now
                else now
            )

            new_until = base + timedelta(days=days)

            update_result = (
                supabase
                .table("users")
                .update(
                    {
                        "is_premium": True,
                        "premium_until": new_until.isoformat(),
                    }
                )
                .eq("user_id", user_id)
                .execute()
            )

            if not update_result.data:
                raise RuntimeError(
                    f"Не вдалося активувати Premium для {user_id}."
                )

            logger.info(
                "Premium granted: user=%s days=%s until=%s",
                user_id,
                days,
                new_until.isoformat(),
            )

            return new_until

        return await _run_db(_db_op)

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
        """Додає завдання в таблицю tasks."""

        valid_categories = {
            "Reading",
            "Use of English",
            "Персональний симулятор помилок (190+)",
        }

        category = category.strip()
        correct_answer = correct_answer.strip().upper()

        if category not in valid_categories:
            raise ValueError(
                "Невірна категорія. Дозволено: "
                "Reading, Use of English, "
                "Персональний симулятор помилок (190+)."
            )

        if correct_answer not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer повинен бути A/B/C/D.")

        if set(options.keys()) != {"A", "B", "C", "D"}:
            raise ValueError(
                "Потрібно передати рівно чотири варіанти A/B/C/D."
            )

        def _db_op() -> Dict[str, Any]:
            result = (
                supabase
                .table("tasks")
                .insert(
                    {
                        "category": category,
                        "sub_category": sub_category.strip(),
                        "section": section.strip() or "NMT",
                        "question_text": question_text.strip(),
                        "options": options,
                        "correct_answer": correct_answer,
                        "explanation": explanation.strip(),
                    }
                )
                .execute()
            )

            if not result.data:
                raise RuntimeError("Supabase не повернув створене питання.")

            return result.data[0]

        return await _run_db(_db_op)

    @staticmethod
    async def get_personalized_tasks(
        user_id: int,
        category: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Повертає питання з пріоритетом помилок користувача.

        Для персонального симулятора бере всі три блоки.
        """

        user_id = int(user_id)
        limit = max(1, min(int(limit), 20))

        def _db_op() -> List[Dict[str, Any]]:
            if category == "personalized":
                task_query = (
                    supabase
                    .table("tasks")
                    .select("*")
                    .eq("section", "NMT")
                )
            else:
                task_query = (
                    supabase
                    .table("tasks")
                    .select("*")
                    .eq("category", category)
                )

            tasks_result = task_query.execute()
            all_tasks = tasks_result.data or []

            if not all_tasks:
                return []

            attempts_result = (
                supabase
                .table("user_attempts")
                .select("task_id,is_correct")
                .eq("user_id", user_id)
                .execute()
            )

            wrong_ids = {
                int(item["task_id"])
                for item in (attempts_result.data or [])
                if not item.get("is_correct")
                and item.get("task_id") is not None
            }

            wrong_tasks = [
                task
                for task in all_tasks
                if int(task["id"]) in wrong_ids
            ]

            other_tasks = [
                task
                for task in all_tasks
                if int(task["id"]) not in wrong_ids
            ]

            random.shuffle(wrong_tasks)
            random.shuffle(other_tasks)

            return (wrong_tasks + other_tasks)[:limit]

        return await _run_db(_db_op)

    @staticmethod
    async def get_express_tasks(limit: int = 5) -> List[Dict[str, Any]]:
        """Повертає короткий стартовий набір із двох основних блоків."""

        limit = max(3, min(int(limit), 5))

        def _db_op() -> List[Dict[str, Any]]:
            result = (
                supabase
                .table("tasks")
                .select("*")
                .in_(
                    "category",
                    ["Reading", "Use of English"],
                )
                .execute()
            )

            tasks = result.data or []
            random.shuffle(tasks)

            return tasks[:limit]

        return await _run_db(_db_op)

    @staticmethod
    async def decrease_test_limit(
        user_id: int,
        current_left: int,
    ) -> bool:
        """Сумісність зі старою логікою."""

        user_id = int(user_id)

        def _db_op() -> bool:
            new_value = max(0, int(current_left) - 1)

            result = (
                supabase
                .table("users")
                .update({"daily_tests_left": new_value})
                .eq("user_id", user_id)
                .execute()
            )

            return bool(result.data)

        return await _run_db(_db_op)

    @staticmethod
    async def consume_test(
        user_id: int,
    ) -> bool:
        """
        Атомарно намагається списати одну безкоштовну спробу
        через SQL RPC.

        Premium-користувачі не обмежуються.
        """

        user_id = int(user_id)

        def _db_op() -> bool:
            result = supabase.rpc(
                "consume_daily_test",
                {"p_user_id": user_id},
            ).execute()

            if isinstance(result.data, bool):
                return result.data

            if isinstance(result.data, list) and result.data:
                value = result.data[0]

                if isinstance(value, dict):
                    return bool(
                        value.get("consume_daily_test", False)
                    )

                return bool(value)

            return False

        try:
            return await _run_db(_db_op)
        except Exception as exc:
            logger.exception(
                "consume_daily_test RPC failed for user %s: %s",
                user_id,
                exc,
            )

            # Безпечний fallback.
            user = await DBClient.get_or_create_user(
                user_id=user_id
            )

            if user.get("is_premium"):
                return True

            left = int(user.get("daily_tests_left") or 0)

            if left <= 0:
                return False

            return await DBClient.decrease_test_limit(
                user_id,
                left,
            )

    @staticmethod
    async def save_attempt(
        user_id: int,
        task_id: int,
        answer: str,
        is_correct: bool,
    ) -> bool:
        """Зберігає відповідь користувача."""

        user_id = int(user_id)
        task_id = int(task_id)

        def _db_op() -> bool:
            attempt_result = (
                supabase
                .table("user_attempts")
                .insert(
                    {
                        "user_id": user_id,
                        "task_id": task_id,
                        "selected_answer": answer.upper(),
                        "is_correct": bool(is_correct),
                    }
                )
                .execute()
            )

            if not attempt_result.data:
                return False

            # Один додатковий update. На Free tier це все ще
            # контрольований semaphore-ом запит.
            user_result = (
                supabase
                .table("users")
                .select("total_tasks_solved")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if user_result.data:
                current = int(
                    user_result.data[0].get("total_tasks_solved") or 0
                )

                (
                    supabase
                    .table("users")
                    .update(
                        {
                            "total_tasks_solved": current + 1,
                            "last_active_at": utc_now().isoformat(),
                        }
                    )
                    .eq("user_id", user_id)
                    .execute()
                )

            return True

        return await _run_db(_db_op)

    @staticmethod
    async def complete_test(
        user_id: int,
    ) -> None:
        """Збільшує лічильник завершених тестів."""

        user_id = int(user_id)

        def _db_op() -> None:
            result = (
                supabase
                .table("users")
                .select("total_tests_passed")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            current = 0

            if result.data:
                current = int(
                    result.data[0].get("total_tests_passed") or 0
                )

            (
                supabase
                .table("users")
                .update(
                    {
                        "total_tests_passed": current + 1,
                        "last_active_at": utc_now().isoformat(),
                    }
                )
                .eq("user_id", user_id)
                .execute()
            )

        await _run_db(_db_op)

    @staticmethod
    async def process_referral(
        new_user_id: int,
        referrer_id: int,
    ) -> bool:
        """
        Прив'язує нового користувача до реферера.

        Premium не видається тут: нагорода видається тільки
        після першого завершеного тесту.
        """

        new_user_id = int(new_user_id)
        referrer_id = int(referrer_id)

        if new_user_id == referrer_id:
            return False

        def _db_op() -> bool:
            result = (
                supabase
                .table("users")
                .select("referrer_id")
                .eq("user_id", new_user_id)
                .limit(1)
                .execute()
            )

            if not result.data:
                return False

            current_referrer = result.data[0].get("referrer_id")

            if current_referrer:
                return False

            referrer_result = (
                supabase
                .table("users")
                .select("user_id")
                .eq("user_id", referrer_id)
                .limit(1)
                .execute()
            )

            if not referrer_result.data:
                return False

            update_result = (
                supabase
                .table("users")
                .update({"referrer_id": referrer_id})
                .eq("user_id", new_user_id)
                .is_("referrer_id", "null")
                .execute()
            )

            return bool(update_result.data)

        return await _run_db(_db_op)

    @staticmethod
    async def complete_referral(
        new_user_id: int,
    ) -> Optional[int]:
        """
        Видає рефереру +3 дні Premium після першого завершеного тесту.

        Повертає ID реферера, якщо нагороду видано.
        """

        new_user_id = int(new_user_id)

        def _db_op() -> Optional[int]:
            result = (
                supabase
                .table("users")
                .select("referrer_id,referral_rewarded")
                .eq("user_id", new_user_id)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            user = result.data[0]
            referrer_id = user.get("referrer_id")

            if not referrer_id or user.get("referral_rewarded"):
                return None

            lock_result = (
                supabase
                .table("users")
                .update({"referral_rewarded": True})
                .eq("user_id", new_user_id)
                .eq("referral_rewarded", False)
                .execute()
            )

            if not lock_result.data:
                return None

            referrer_result = (
                supabase
                .table("users")
                .select("referrals_count")
                .eq("user_id", int(referrer_id))
                .limit(1)
                .execute()
            )

            if not referrer_result.data:
                return None

            current_count = int(
                referrer_result.data[0].get("referrals_count") or 0
            )

            (
                supabase
                .table("users")
                .update(
                    {
                        "referrals_count": current_count + 1,
                    }
                )
                .eq("user_id", int(referrer_id))
                .execute()
            )

            return int(referrer_id)

        referrer_id = await _run_db(_db_op)

        if referrer_id:
            await DBClient.grant_premium(
                referrer_id,
                days=3,
            )

        return referrer_id

    @staticmethod
    async def get_all_user_ids() -> List[int]:
        """Повертає активних користувачів для аудиту."""

        def _db_op() -> List[int]:
            result = (
                supabase
                .table("users")
                .select("user_id")
                .eq("is_active", True)
                .execute()
            )

            return [
                int(item["user_id"])
                for item in (result.data or [])
                if item.get("user_id") is not None
            ]

        return await _run_db(_db_op)

    @staticmethod
    async def set_user_active_status(
        user_id: int,
        is_active: bool,
    ) -> bool:
        """Змінює активність користувача."""

        def _db_op() -> bool:
            result = (
                supabase
                .table("users")
                .update({"is_active": bool(is_active)})
                .eq("user_id", int(user_id))
                .execute()
            )

            return bool(result.data)

        return await _run_db(_db_op)

    @staticmethod
    async def get_admin_stats() -> Dict[str, int]:
        """Статистика без завантаження всього контенту в пам'ять."""

        def _db_op() -> Dict[str, int]:
            users_result = (
                supabase
                .table("users")
                .select(
                    "user_id,is_active,is_premium,premium_until"
                )
                .execute()
            )

            tasks_result = (
                supabase
                .table("tasks")
                .select("id")
                .execute()
            )

            users = users_result.data or []
            tasks = tasks_result.data or []

            now = utc_now()

            premium_users = 0

            for user in users:
                premium_until = parse_datetime(
                    user.get("premium_until")
                )

                if (
                    user.get("is_premium")
                    and (
                        premium_until is None
                        or premium_until > now
                    )
                ):
                    premium_users += 1

            total_users = len(users)

            return {
                "total_users": total_users,
                "active_users": sum(
                    1 for user in users
                    if user.get("is_active", True)
                ),
                "blocked_users": sum(
                    1 for user in users
                    if not user.get("is_active", True)
                ),
                "premium_users": premium_users,
                "total_questions": len(tasks),
            }

        return await _run_db(_db_op)

    @staticmethod
    async def get_retention_candidates(
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Знаходить користувачів, які не заходили понад 24 години."""

        cutoff = utc_now() - timedelta(hours=24)

        def _db_op() -> List[Dict[str, Any]]:
            result = (
                supabase
                .table("users")
                .select(
                    "user_id,last_active_at,last_reminder_at"
                )
                .eq("is_active", True)
                .lt("last_active_at", cutoff.isoformat())
                .limit(limit)
                .execute()
            )

            candidates: List[Dict[str, Any]] = []

            for user in result.data or []:
                last_reminder = parse_datetime(
                    user.get("last_reminder_at")
                )

                if (
                    last_reminder is None
                    or last_reminder <= cutoff
                ):
                    candidates.append(user)

            return candidates

        return await _run_db(_db_op)

    @staticmethod
    async def set_last_reminder(
        user_id: int,
    ) -> bool:
        def _db_op() -> bool:
            result = (
                supabase
                .table("users")
                .update(
                    {
                        "last_reminder_at": utc_now().isoformat()
                    }
                )
                .eq("user_id", int(user_id))
                .execute()
            )

            return bool(result.data)

        return await _run_db(_db_op)

    @staticmethod
    async def get_user_profile(
        user_id: int,
    ) -> Dict[str, Any]:
        def _db_op() -> Dict[str, Any]:
            result = (
                supabase
                .table("users")
                .select(
                    "user_id,username,first_name,"
                    "is_premium,premium_until,"
                    "total_tasks_solved,total_tests_passed,"
                    "streak,referrals_count"
                )
                .eq("user_id", int(user_id))
                .limit(1)
                .execute()
            )

            return result.data[0] if result.data else {}

        return await _run_db(_db_op)

    @staticmethod
    async def register_payment(
        user_id: int,
        payload: str,
        charge_id: str,
        amount: int,
    ) -> bool:
        """
        Реєструє Telegram Stars payment.

        UNIQUE(charge_id) у БД захищає від повторного нарахування.
        """

        def _db_op() -> bool:
            try:
                result = (
                    supabase
                    .table("payments")
                    .insert(
                        {
                            "user_id": int(user_id),
                            "payload": payload,
                            "telegram_payment_charge_id": charge_id,
                            "amount": int(amount),
                            "currency": "XTR",
                        }
                    )
                    .execute()
                )

                return bool(result.data)

            except Exception as exc:
                # Найчастіший випадок тут — duplicate charge_id.
                logger.warning(
                    "Payment already registered or rejected: %s",
                    exc,
                )
                return False

        return await _run_db(_db_op)


db_client = DBClient()

get_or_create_user = DBClient.get_or_create_user
mark_user_inactive = lambda user_id: DBClient.set_user_active_status(
    user_id,
    False,
)
decrease_test_limit = DBClient.decrease_test_limit
save_attempt = DBClient.save_attempt
