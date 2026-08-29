import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class DBClient:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # ================= USER MANAGEMENT =================
    @classmethod
    async def get_or_create_user(
        cls, 
        user_id: int, 
        username: Optional[str] = "", 
        first_name: Optional[str] = "", 
        referrer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Отримує користувача або створює нового/оновлює статус активності."""
        try:
            res = cls.supabase.table("users").select("*").eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                # Якщо користувач повернувся, робимо його знову активним
                if not res.data[0].get("is_active", True):
                    cls.supabase.table("users").update({"is_active": True}).eq("user_id", user_id).execute()
                return res.data[0]

            # Створення нового користувача
            new_user = {
                "user_id": user_id,
                "username": username or "",
                "first_name": first_name or "",
                "streak": 1,
                "xp": 0,
                "is_premium": False,
                "is_active": True,
                "referred_by": referrer_id if (referrer_id and referrer_id != user_id) else None,
                "referrals_count": 0
            }
            inserted = cls.supabase.table("users").insert(new_user).execute()
            
            if referrer_id and referrer_id != user_id:
                cls._process_referral(referrer_id)

            return inserted.data[0] if inserted.data else new_user
        except Exception as e:
            logger.error(f"Помилка в get_or_create_user: {e}", exc_info=True)
            return {
                "user_id": user_id, 
                "username": username or "", 
                "first_name": first_name or "", 
                "streak": 1, 
                "xp": 0, 
                "is_premium": False,
                "is_active": True,
                "referrals_count": 0
            }

    @classmethod
    def _process_referral(cls, referrer_id: int):
        """Обробка реферальної системи."""
        try:
            res = cls.supabase.table("users").select("*").eq("user_id", referrer_id).execute()
            if not res.data:
                return
            
            user = res.data[0]
            new_count = user.get("referrals_count", 0) + 1
            is_premium = user.get("is_premium", False)

            if new_count % 2 == 0:
                is_premium = True

            cls.supabase.table("users").update({
                "referrals_count": new_count,
                "is_premium": is_premium
            }).eq("user_id", referrer_id).execute()
        except Exception as e:
            logger.error(f"Помилка в _process_referral: {e}", exc_info=True)

    @classmethod
    async def set_user_active_status(cls, user_id: int, is_active: bool):
        """Оновлює статус: чи активний користувач, чи заблокував бота."""
        try:
            cls.supabase.table("users").update({"is_active": is_active}).eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Помилка set_user_active_status для {user_id}: {e}")

    @classmethod
    async def get_all_user_ids(cls) -> List[int]:
        """Отримує список ID усіх користувачів для перевірки/розсилки."""
        try:
            res = cls.supabase.table("users").select("user_id").execute()
            return [row["user_id"] for row in res.data] if res.data else []
        except Exception as e:
            logger.error(f"Помилка get_all_user_ids: {e}")
            return []

    # ================= STATS FOR ADMIN =================
    @classmethod
    async def get_admin_stats(cls) -> Dict[str, int]:
        """Отримує точні дані про користувачів без помилок підрахунку."""
        stats = {
            "total_users": 0, 
            "active_users": 0, 
            "blocked_users": 0, 
            "premium_users": 0, 
            "total_questions": 0
        }
        try:
            # Отримуємо всіх користувачів для точного мануального підрахунку
            users_res = cls.supabase.table("users").select("user_id, is_premium, is_active").execute()
            users_data = users_res.data or []

            stats["total_users"] = len(users_data)
            stats["premium_users"] = sum(1 for u in users_data if u.get("is_premium"))
            stats["active_users"] = sum(1 for u in users_data if u.get("is_active", True))
            stats["blocked_users"] = stats["total_users"] - stats["active_users"]

            # Кількість питань
            q_res = cls.supabase.table("questions").select("id").execute()
            stats["total_questions"] = len(q_res.data or [])
        except Exception as e:
            logger.error(f"Помилка при отриманні адмін-статистики: {e}", exc_info=True)
        return stats

    # ================= QUESTIONS MANAGEMENT =================
    @classmethod
    async def add_question(cls, topic: str, difficulty: int, question_text: str, options: list, correct_option: int, explanation: str = "") -> bool:
        try:
            payload = {
                "topic": topic,
                "difficulty": difficulty,
                "question_text": question_text,
                "options": options,
                "correct_option": correct_option,
                "explanation": explanation
            }
            cls.supabase.table("questions").insert(payload).execute()
            return True
        except Exception as e:
            logger.error(f"Помилка add_question: {e}", exc_info=True)
            return False
