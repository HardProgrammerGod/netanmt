import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in raw_admins.split(",") if i.strip().isdigit()]
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
