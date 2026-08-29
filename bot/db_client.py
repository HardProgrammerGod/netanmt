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
        """Отримує користувача або створює нового з реферальною системою."""
        try:
            res = cls.supabase.table("users").select("*").eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]

            # Створення нового користувача
            new_user = {
                "user_id": user_id,
                "username": username or "",
                "first_name": first_name or "",
                "streak": 1,
                "xp": 0,
                "is_premium": False,
                "referred_by": referrer_id if (referrer_id and referrer_id != user_id) else None,
                "referrals_count": 0
            }
            inserted = cls.supabase.table("users").insert(new_user).execute()
            
            # Якщо є реферер — зараховуємо йому реферала
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
                "referrals_count": 0
            }

    @classmethod
    def _process_referral(cls, referrer_id: int):
        """Збільшує лічильник рефералів рефереру та відкриває Premium за кожні 2 друзів."""
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
    async def add_xp(cls, user_id: int, amount: int = 10):
        """Додає XP за правильні відповіді."""
        try:
            res = cls.supabase.table("users").select("xp").eq("user_id", user_id).execute()
            if res.data:
                current_xp = res.data[0].get("xp", 0)
                cls.supabase.table("users").update({"xp": current_xp + amount}).eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Помилка add_xp: {e}", exc_info=True)

    # ================= STATS FOR ADMIN =================
    @classmethod
    async def get_admin_stats(cls) -> Dict[str, int]:
        """Повертає точну статистику бота для адмін-панелі."""
        stats = {"total_users": 0, "premium_users": 0, "total_questions": 0}
        try:
            users_res = cls.supabase.table("users").select("user_id", count="exact").execute()
            stats["total_users"] = users_res.count if users_res.count is not None else len(users_res.data or [])

            premium_res = cls.supabase.table("users").select("user_id", count="exact").eq("is_premium", True).execute()
            stats["premium_users"] = premium_res.count if premium_res.count is not None else len(premium_res.data or [])

            q_res = cls.supabase.table("questions").select("id", count="exact").execute()
            stats["total_questions"] = q_res.count if q_res.count is not None else len(q_res.data or [])
        except Exception as e:
            logger.error(f"Помилка при отриманні адмін-статистики: {e}", exc_info=True)
        return stats

    # ================= QUESTIONS MANAGEMENT =================
    @classmethod
    async def add_question(cls, topic: str, difficulty: int, question_text: str, options: list, correct_option: int, explanation: str = "") -> bool:
        """Додає питання в базу даних."""
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

    @classmethod
    async def get_questions_by_difficulty(cls, difficulty: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Отримує питання за рівнем складності."""
        try:
            res = cls.supabase.table("questions").select("*").eq("difficulty", difficulty).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Помилка get_questions_by_difficulty: {e}", exc_info=True)
            return []

    @classmethod
    async def get_question_by_id(cls, question_id: int) -> Optional[Dict[str, Any]]:
        """Отримує конкретне питання за ID."""
        try:
            res = cls.supabase.table("questions").select("*").eq("id", question_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Помилка get_question_by_id: {e}", exc_info=True)
            return None
