import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in raw_admins.split(",") if i.strip().isdigit()]

PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "").strip()

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN відсутній у змінних оточення!")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Данні підключення Supabase відсутні у змінних оточення!")
