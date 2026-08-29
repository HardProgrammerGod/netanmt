import asyncio
import logging
from datetime import date
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Ініціалізація клієнта Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class DBClient:
    """Клас для безпечної взаємодії з БД Supabase через асинхронні обгортки."""

    @staticmethod
    async def get_or_create_user(tg_id: Optional[int] = None, username: str = "", first_name: str = "", user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Асинхронно отримує або створює користувача в БД Supabase.
        Підтримує передачу і tg_id, і user_id для гнучкості.
        """
        target_id = tg_id if tg_id is not None else user_id
        if target_id is None:
            raise ValueError("Потрібно вказати tg_id або user_id")

        today = str(date.today())

        def _db_op():
            try:
                # Шукаємо користувача по user_id в Supabase
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
                    logger.info(f"✅ Користувача {target_id} успішно додано в Supabase!")

                    # Спроба оновити загальну статистику
                    try:
                        stats = supabase.table("global_stats").select("total_users_count").eq("id", 1).execute()
                        if stats.data:
                            current_total = stats.data[0].get("total_users_count", 0)
                            supabase.table("global_stats").update({"total_users_count": current_total + 1}).eq("id", 1).execute()
                    except Exception as stats_err:
                        logger.warning(f"Не вдалося оновити global_stats: {stats_err}")

                    return insert_res.data[0] if insert_res.data else new_user

                user = res.data[0]
                updates = {}

                # Відновлення активності
                if not user.get("is_active", True):
                    updates["is_active"] = True
                    user["is_active"] = True

                # Скидання денного ліміту
                if user.get("last_test_date") != today:
                    updates["daily_tests_left"] = 3
                    updates["last_test_date"] = today
                    user["daily_tests_left"] = 3
                    user["last_test_date"] = today

                if updates:
                    supabase.table("users").update(updates).eq("user_id", int(target_id)).execute()

                return user

            except Exception as e:
                logger.error(f"❌ Помилка в get_or_create_user для {target_id}: {e}", exc_info=True)
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
    async def mark_user_inactive(user_id: int):
        """Маркує користувача як неактивного (Soft Delete при блокуванні бота)."""
        def _db_op():
            try:
                supabase.table("users").update({"is_active": False}).eq("user_id", int(user_id)).execute()
            except Exception as e:
                logger.error(f"Error marking user {user_id} inactive: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def get_full_test_tasks(category: str, sub_category: str) -> List[Dict[str, Any]]:
        """Отримує пул питань з таблиці tasks."""
        def _db_op():
            try:
                res = supabase.table("tasks") \
                    .select("id, category, sub_category, section, question_text, options, correct_answer, explanation") \
                    .eq("category", category) \
                    .eq("sub_category", sub_category) \
                    .order("id") \
                    .execute()
                return res.data or []
            except Exception as e:
                logger.error(f"Помилка завантаження тасків: {e}")
                return []

        return await asyncio.to_thread(_db_op)

    @staticmethod
    async def decrease_test_limit(tg_id: int, current_left: int):
        """Зменшує ліміт спроб користувача на 1."""
        def _db_op():
            try:
                supabase.table("users").update({
                    "daily_tests_left": max(0, current_left - 1)
                }).eq("user_id", int(tg_id)).execute()
            except Exception as e:
                logger.error(f"Помилка зменшення ліміту для {tg_id}: {e}")

        await asyncio.to_thread(_db_op)

    @staticmethod
    async def save_attempt(user_id: int, task_id: int, answer: str, is_correct: bool):
        """Фіксує відповідь користувача в таблиці user_attempts."""
        def _db_op():
            try:
                supabase.table("user_attempts").insert({
                    "user_id": int(user_id),
                    "task_id": task_id,
                    "selected_answer": answer,
                    "is_correct": is_correct
                }).execute()
            except Exception as e:
                logger.error(f"Помилка збереження спроби для {user_id}: {e}")

        await asyncio.to_thread(_db_op)


# --- Синоніми та функції верхнього рівня для повної сумісності ---
db_client = DBClient()

get_or_create_user = DBClient.get_or_create_user
mark_user_inactive = DBClient.mark_user_inactive
get_full_test_tasks = DBClient.get_full_test_tasks
decrease_test_limit = DBClient.decrease_test_limit
save_attempt = DBClient.save_attempt
