import random
from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DBClient:
    @staticmethod
    def get_or_create_user(user_id: int, username: str, first_name: str, referrer_id: int = None):
        res = supabase.table("users").select("*").eq("id", user_id).execute()
        if not res.data:
            data = {
                "id": user_id,
                "username": username,
                "first_name": first_name,
                "referrer_id": referrer_id if referrer_id and referrer_id != user_id else None
            }
            res = supabase.table("users").insert(data).execute()
            if referrer_id and referrer_id != user_id:
                ref_res = supabase.table("users").select("xp").eq("id", referrer_id).execute()
                if ref_res.data:
                    supabase.table("users").update({"xp": ref_res.data[0]["xp"] + 100}).eq("id", referrer_id).execute()
            return res.data[0], True
        return res.data[0], False

    @staticmethod
    def get_next_question(user_id: int):
        answered_res = supabase.table("user_answers").select("question_id").eq("user_id", user_id).execute()
        answered_ids = [r["question_id"] for r in answered_res.data]

        query = supabase.table("questions").select("*")
        if answered_ids:
            query = query.not_.filter("id", "in", f"({','.join(answered_ids)})")

        res = query.execute()
        if not res.data:
            res = supabase.table("questions").select("*").execute()
            
        return random.choice(res.data) if res.data else None

    @staticmethod
    def record_answer(user_id: int, question_id: str, is_correct: bool):
        supabase.table("user_answers").insert({
            "user_id": user_id,
            "question_id": question_id,
            "is_correct": is_correct
        }).execute()

        if is_correct:
            user_res = supabase.table("users").select("xp").eq("id", user_id).execute()
            if user_res.data:
                supabase.table("users").update({"xp": user_res.data[0]["xp"] + 15}).eq("id", user_id).execute()

    @staticmethod
    def get_leaderboard():
        res = supabase.table("weekly_leaderboard").select("*").limit(10).execute()
        return res.data

    @staticmethod
    def add_question(topic: str, difficulty: int, question_text: str, options: list, correct_option: int, explanation: str = ""):
        data = {
            "topic": topic.lower().strip(),
            "difficulty": int(difficulty),
            "question_text": question_text,
            "options": options,
            "correct_option": int(correct_option),
            "explanation": explanation
        }
        return supabase.table("questions").insert(data).execute()

    @staticmethod
    def get_user_roadmap(user_id: int):
        """Отримує всі теми та статус їх відкриття для юзера"""
        topics = supabase.table("topics").select("*").order("order_index").execute().data
        user_progress = supabase.table("user_topics").select("*").eq("user_id", user_id).execute().data
        
        completed_topics = {p["topic_id"] for p in user_progress if p["is_completed"]}

        roadmap = []
        # Перша тема відкрита завжди, наступні — якщо пройдена попередня
        previous_completed = True 

        for t in topics:
            is_completed = t["id"] in completed_topics
            is_unlocked = previous_completed

            roadmap.append({
                "id": t["id"],
                "title": t["title"],
                "icon": t["icon"],
                "order": t["order_index"],
                "is_completed": is_completed,
                "is_unlocked": is_unlocked
            })
            previous_completed = is_completed

        return roadmap

    @staticmethod
    def unlock_topic(user_id: int, topic_id: str):
        """Позначає тему як пройдену"""
        supabase.table("user_topics").upsert({
            "user_id": user_id,
            "topic_id": topic_id,
            "is_completed": True
        }).execute()

    @staticmethod
    def get_test_questions(topic_id: str, limit: int = 5):
        """Бере случайные вопросы для теста-пропуска"""
        res = supabase.table("questions").select("*").eq("topic", topic_id).limit(limit).execute()
        return res.data
