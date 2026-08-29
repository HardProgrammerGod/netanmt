import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Сповіщення адмінів (список ID через кому, наприклад: "123456,789012")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

# Перевірка критичних змінних при старті
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено у змінних оточення!")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Налаштування Supabase відсутні у змінних оточення!")
