import os
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise ValueError(
            f"❌ Критична змінна оточення {name} не знайдена."
        )

    return value


BOT_TOKEN: str = _get_required_env("BOT_TOKEN")
SUPABASE_URL: str = _get_required_env("SUPABASE_URL")
SUPABASE_KEY: str = _get_required_env("SUPABASE_KEY")
WEBHOOK_BASE_URL: str = _get_required_env("WEBHOOK_BASE_URL")


def _parse_admin_ids(raw_value: str) -> List[int]:
    result: List[int] = []

    for item in raw_value.split(","):
        item = item.strip()

        if not item:
            continue

        try:
            result.append(int(item))
        except ValueError:
            raise ValueError(
                f"❌ Некоректний ADMIN_IDS елемент: {item!r}"
            )

    return result


ADMIN_IDS: List[int] = _parse_admin_ids(
    os.getenv("ADMIN_IDS", "")
)

WEBHOOK_PATH: str = "/webhook"

PORT: int = int(
    os.getenv("PORT", "8080")
)

WEBHOOK_URL: str = (
    f"{WEBHOOK_BASE_URL.rstrip('/')}{WEBHOOK_PATH}"
)

WEB_APP_URL: str = os.getenv(
    "WEB_APP_URL",
    ""
).strip()


# ------------------------------------------------------------
# Product configuration
# ------------------------------------------------------------

FREE_DAILY_QUIZ_LIMIT: int = 3

EXPRESS_QUIZ_LENGTH: int = 5

REGULAR_QUIZ_LENGTH: int = 5

FULL_SIMULATION_LENGTH: int = 32

PREMIUM_3_DAYS: int = 3

PREMIUM_30_DAYS: int = 30

PREMIUM_3_DAYS_PRICE: int = 49

PREMIUM_30_DAYS_PRICE: int = 199

REFERRAL_PREMIUM_DAYS: int = 3

# Manual payment / sales
MANAGER_USERNAME: str = os.getenv("MANAGER_USERNAME", "nnopkam").strip().lstrip("@")
MANAGER_DISCOUNT_PERCENT: int = int(os.getenv("MANAGER_DISCOUNT_PERCENT", "27"))

# Retention: the background loop may wake hourly, but a user receives at
# most one reminder per day and only around the configured Kyiv hour.
RETENTION_INACTIVE_HOURS: int = int(os.getenv("RETENTION_INACTIVE_HOURS", "20"))
RETENTION_COOLDOWN_HOURS: int = int(os.getenv("RETENTION_COOLDOWN_HOURS", "20"))
RETENTION_SEND_HOUR_KYIV: int = int(os.getenv("RETENTION_SEND_HOUR_KYIV", "18"))

# Premium-only deep practice
PREMIUM_FOCUS_QUIZ_LENGTH: int = int(os.getenv("PREMIUM_FOCUS_QUIZ_LENGTH", "10"))


# ------------------------------------------------------------
# NMT categories
# ------------------------------------------------------------

CATEGORY_READING = "Reading"

CATEGORY_USE_OF_ENGLISH = "Use of English"

CATEGORY_PERSONALIZED = "Персональний симулятор помилок"

ALLOWED_CATEGORIES = {
    CATEGORY_READING,
    CATEGORY_USE_OF_ENGLISH,
    CATEGORY_PERSONALIZED,
}


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

if not ADMIN_IDS:
    # Це не критична помилка для користувачів,
    # але попереджаємо в логах у main.py.
    pass
