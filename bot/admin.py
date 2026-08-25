import json
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.config import ADMIN_IDS
from bot.db_client import DBClient

admin_router = Router()

@admin_router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_admin(message: types.Message):
    await message.answer("🛠 <b>Админ-панель</b>\nОтправь JSON-файл с вопросами для массовой загрузки.", parse_mode="HTML")

@admin_router.message(F.document, F.from_user.id.in_(ADMIN_IDS))
async def upload_json_questions(message: types.Message, bot):
    if not message.document.file_name.endswith(".json"):
        await message.answer("Отправь файл в формате .json!")
        return

    file = await bot.get_file(message.document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    
    try:
        questions = json.loads(file_bytes.read().decode("utf-8"))
        count = 0
        for q in questions:
            DBClient.add_question(
                topic=q["topic"],
                difficulty=q["difficulty"],
                question_text=q["question_text"],
                options=q["options"],
                correct_option=q["correct_option"],
                explanation=q.get("explanation", "")
            )
            count += 1
        await message.answer(f"🎉 Загружено <b>{count}</b> вопросов в Supabase!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
