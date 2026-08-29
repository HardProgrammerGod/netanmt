import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

raw_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
if raw_admin_ids:
    for item in raw_admin_ids.split(","):
        item = item.strip()
        if item.isdigit():
            ADMIN_IDS.append(int(item))

# Перевірка критичних змінних при старті
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено у змінних оточення!")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Налаштування Supabase відсутні у змінних оточення!")

WEB_APP_URL = os.getenv("WEB_APP_URL", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "nnopkam").replace("@", "")
