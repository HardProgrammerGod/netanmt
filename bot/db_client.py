import asyncio
import logging
from datetime import date
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class DBClient:
    """Клас для безпечної взаємодії з БД Supabase."""

    @staticmethod
    async def get_or_create_user(tg_id: Optional[int] = None, username: str = "", first_name: str = "", user_id: Optional[int] = None) -> Dict[str, Any]:
        target_id = tg_id if tg_id is not None else user_id
        if target_id is None:
            raise ValueError("Потрібно вказати tg_id або user_id")

        today = str(date.today())

        def _db_op():
            try:
                res = supabase.table("users").select("*").eq("user_id", int(target_id)).execute()

                if not res.data:
                    new_user = {
                        "user_id": int(target_id),
                        "username": username or "",
                        "first_name": first_name or "Учень",
                        "daily_tests_left": 3,
                        "last_test_date": today,
                        "is_premium": False,
                        "is_active": True,
                        "total_tests_passed": 0,
                        "referrals_count": 0
                    }
                    insert_res = supabase.table("users").insert(new_user).execute()
                    logger.info(f"✅ Користувача {target_id} додано в Supabase!")
                    return insert_res.data[0] if insert_res.data else new_user

                user = res.data[0]
                updates = {}

                if not user.get("is_active", True):
                    updates["is_active"] = True
                    user["is_active"] = True

                if user.get("last_test_date") != today:
                    updates["daily_tests_left"] = 3
                    updates["last_test_date"] = today
                    user["daily_tests_left"] = 3
                    user["last_test_date"] = today

                if updates:
                    supabase.table("users").update(updates).eq("user_id", int(target_id)).execute()

                return user

            except Exception as e:
                logger.error(f"❌ Помилка get_or_create_user ({target_id}): {e}", exc_info=True)
                return {
                    "user_id": int(target_id),
                    "username": username or "",
                    "first_name": first_name or "Учень",
                    "daily_tests_left": 3,
                    "is_active": True,
                    "is_premium": False
                }

        return await asyncio.to_thread(_db_op)

    @staticmethod
    async def grant_premium(user_id: int):
        """Активація преміум-підписки після успішної сплати Stars."""
        def _db_op():
            try:
                supabase.table("users").update({"is_premium": True}).eq("user_id", int(user_id)).execute()
                logger.info(f"🌟 Преміум активовано для користувача {user_id}")
            except Exception as e:
                logger.error(f"Помилка активації преміуму для {user_id}: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def get_personalized_tasks(user_id: int, category: str, sub_category: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Персоналізований підбір питань НМТ:
        Враховує темні плями (попередні помилки) користувача з user_attempts.
        """
        def _db_op():
            try:
                # Отримуємо всі таски заданої категорії НМТ
                query = supabase.table("tasks").select("*").eq("category", category)
                if sub_category:
                    query = query.eq("sub_category", sub_category)
                tasks_res = query.execute()
                all_tasks = tasks_res.data or []

                if not all_tasks:
                    return []

                # Отримуємо ID завдань, де у користувача були помилки
                attempts_res = supabase.table("user_attempts") \
                    .select("task_id, is_correct") \
                    .eq("user_id", int(user_id)) \
                    .execute()
                
                wrong_task_ids = {a["task_id"] for a in (attempts_res.data or []) if not a.get("is_correct")}

                # Пріоритезуємо теми/запитання, де учень робив помилки
                wrong_tasks = [t for t in all_tasks if t["id"] in wrong_task_ids]
                other_tasks = [t for t in all_tasks if t["id"] not in wrong_task_ids]

                # Міксуємо: спершу складні для учня питання, потім інші
                result = (wrong_tasks + other_tasks)[:limit]
                return result

            except Exception as e:
                logger.error(f"Помилка формування персоналізованого тесту: {e}")
                return []

        return await asyncio.to_thread(_db_op)

    @staticmethod
    async def add_task(category: str, sub_category: str, section: str, question_text: str, options: dict, correct_answer: str, explanation: str = ""):
        """Додавання нового питання НМТ з адмінки."""
        def _db_op():
            try:
                supabase.table("tasks").insert({
                    "category": category,
                    "sub_category": sub_category,
                    "section": section,
                    "question_text": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation
                }).execute()
            except Exception as e:
                logger.error(f"Помилка додавання таску: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def decrease_test_limit(tg_id: int, current_left: int):
        def _db_op():
            try:
                supabase.table("users").update({"daily_tests_left": max(0, current_left - 1)}).eq("user_id", int(tg_id)).execute()
            except Exception as e:
                logger.error(f"Помилка зменшення ліміту {tg_id}: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def save_attempt(user_id: int, task_id: int, answer: str, is_correct: bool):
        def _db_op():
            try:
                supabase.table("user_attempts").insert({
                    "user_id": int(user_id),
                    "task_id": task_id,
                    "selected_answer": answer,
                    "is_correct": is_correct
                }).execute()
            except Exception as e:
                logger.error(f"Помилка збереження спроби {user_id}: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def mark_user_inactive(user_id: int):
        def _db_op():
            try:
                supabase.table("users").update({"is_active": False}).eq("user_id", int(user_id)).execute()
            except Exception as e:
                logger.error(f"Error marking user {user_id} inactive: {e}")

        await asyncio.to_thread(_db_op)


db_client = DBClient()
get_or_create_user = DBClient.get_or_create_user
mark_user_inactive = DBClient.mark_user_inactive
decrease_test_limit = DBClient.decrease_test_limit
save_attempt = DBClient.save_attempt
