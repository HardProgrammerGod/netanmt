import random
import logging
from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class DBClient:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # --- Юзери та Рефералка ---

    @classmethod
    def get_or_create_user(cls, user_id: int, username: str, first_name: str, referrer_id: int = None):
        try:
            res = cls.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not res.data:
                valid_referrer = referrer_id if (referrer_id and referrer_id != user_id) else None
                
                data = {
                    "id": user_id,
                    "username": username or "",
                    "first_name": first_name or "",
                    "referrer_id": valid_referrer,
                    "xp": 0,
                    "energy": 5,
                    "is_premium": False
                }
                res = cls.supabase.table("users").insert(data).execute()
                
                # Бонус рефералу (+100 XP)
                if valid_referrer:
                    try:
                        ref_res = cls.supabase.table("users").select("xp").eq("id", valid_referrer).execute()
                        if ref_res.data:
                            current_xp = ref_res.data[0].get("xp", 0)
                            cls.supabase.table("users").update({"xp": current_xp + 100}).eq("id", valid_referrer).execute()
                    except Exception as ref_err:
                        logger.error(f"Помилка нарахування XP рефералу {valid_referrer}: {ref_err}")

                return res.data[0], True # Новий юзер
                
            return res.data[0], False # Існуючий юзер
        except Exception as e:
            logger.error(f"Помилка у get_or_create_user: {e}")
            return None, False

    @classmethod
    def set_premium(cls, user_id: int):
        try:
            cls.supabase.table("users").update({"is_premium": True, "energy": 999}).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Помилка активації Premium: {e}")
            return False

    # --- Питання та Відповіді ---

    @classmethod
    def get_next_question(cls, user_id: int):
        try:
            answered_res = cls.supabase.table("user_answers").select("question_id").eq("user_id", user_id).execute()
            answered_ids = [r["question_id"] for r in answered_res.data] if answered_res.data else []

            query = cls.supabase.table("questions").select("*")
            if answered_ids:
                query = query.not_.filter("id", "in", f"({','.join(map(str, answered_ids))})")

            res = query.execute()
            if not res.data:
                res = cls.supabase.table("questions").select("*").execute()
                
            return random.choice(res.data) if res.data else None
        except Exception as e:
            logger.error(f"Помилка у get_next_question: {e}")
            return None

    @classmethod
    def record_answer(cls, user_id: int, question_id: str, is_correct: bool):
        try:
            cls.supabase.table("user_answers").insert({
                "user_id": user_id,
                "question_id": question_id,
                "is_correct": is_correct
            }).execute()

            if is_correct:
                user_res = cls.supabase.table("users").select("xp").eq("id", user_id).execute()
                if user_res.data:
                    current_xp = user_res.data[0].get("xp", 0)
                    cls.supabase.table("users").update({"xp": current_xp + 15}).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Помилка у record_answer: {e}")

    @classmethod
    def add_question(cls, topic: str, difficulty: int, question_text: str, options: list, correct_option: int, explanation: str = ""):
        try:
            data = {
                "topic": topic.lower().strip(),
                "difficulty": int(difficulty),
                "question_text": question_text,
                "options": options,
                "correct_option": int(correct_option),
                "explanation": explanation
            }
            return cls.supabase.table("questions").insert(data).execute()
        except Exception as e:
            logger.error(f"Помилка у add_question: {e}")
            return None

    # --- Дорожня карта та Тести ---

    @classmethod
    def get_user_roadmap(cls, user_id: int):
        try:
            topics = cls.supabase.table("topics").select("*").order("order_index").execute().data or []
            user_progress = cls.supabase.table("user_topics").select("*").eq("user_id", user_id).execute().data or []
            
            completed_topics = {p["topic_id"] for p in user_progress if p.get("is_completed")}

            roadmap = []
            previous_completed = True 

            for t in topics:
                is_completed = t["id"] in completed_topics
                is_unlocked = previous_completed

                roadmap.append({
                    "id": t["id"],
                    "title": t["title"],
                    "icon": t.get("icon", "📚"),
                    "order": t["order_index"],
                    "is_completed": is_completed,
                    "is_unlocked": is_unlocked
                })
                previous_completed = is_completed

            return roadmap
        except Exception as e:
            logger.error(f"Помилка у get_user_roadmap: {e}")
            return []

    @classmethod
    def unlock_topic(cls, user_id: int, topic_id: str):
        try:
            cls.supabase.table("user_topics").upsert({
                "user_id": user_id,
                "topic_id": topic_id,
                "is_completed": True
            }).execute()
        except Exception as e:
            logger.error(f"Помилка у unlock_topic: {e}")

    @classmethod
    def get_test_questions(cls, topic_id: str, limit: int = 5):
        try:
            res = cls.supabase.table("questions").select("*").eq("topic", topic_id).limit(limit).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Помилка у get_test_questions: {e}")
            return []

    # --- Лідерборд ---

    @classmethod
    def get_leaderboard(cls):
        try:
            res = cls.supabase.table("weekly_leaderboard").select("*").limit(10).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Помилка у get_leaderboard: {e}")
            return []
