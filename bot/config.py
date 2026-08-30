import os
from typing import Final

from dotenv import load_dotenv


load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"❌ Змінна оточення {name} не знайдена.")
    return value


def _parse_admin_ids(raw: str) -> list[int]:
    result: list[int] = []

    for item in raw.split(","):
        item = item.strip()

        if item.isdigit():
            result.append(int(item))

    return result


BOT_TOKEN: Final[str] = _required("BOT_TOKEN")
SUPABASE_URL: Final[str] = _required("SUPABASE_URL")
SUPABASE_KEY: Final[str] = _required("SUPABASE_KEY")

ADMIN_IDS: Final[list[int]] = _parse_admin_ids(
    os.getenv("ADMIN_IDS", "")
)

WEB_APP_URL: Final[str] = os.getenv("WEB_APP_URL", "").strip()

ADMIN_USERNAME: Final[str] = (
    os.getenv("ADMIN_USERNAME", "nnopkam")
    .strip()
    .lstrip("@")
)

PORT: Final[int] = int(os.getenv("PORT", "8080"))

WEBHOOK_PATH: Final[str] = "/webhook"

WEBHOOK_SECRET: Final[str] = os.getenv(
    "WEBHOOK_SECRET",
    "change-this-webhook-secret",
).strip()

RENDER_EXTERNAL_URL: Final[str] = os.getenv(
    "RENDER_EXTERNAL_URL",
    "",
).strip()

CUSTOM_WEBHOOK_URL: Final[str] = os.getenv(
    "WEBHOOK_URL",
    "",
).strip()


def get_webhook_url() -> str:
    """
    Формує публічний HTTPS URL webhook.

    Пріоритет:
    1. WEBHOOK_URL
    2. RENDER_EXTERNAL_URL
    """
    base_url = CUSTOM_WEBHOOK_URL or RENDER_EXTERNAL_URL

    if not base_url:
        raise ValueError(
            "❌ Не знайдено WEBHOOK_URL або RENDER_EXTERNAL_URL. "
            "Для webhook потрібен публічний HTTPS URL."
        )

    base_url = base_url.rstrip("/")

    if not base_url.startswith("https://"):
        raise ValueError(
            "❌ WEBHOOK_URL / RENDER_EXTERNAL_URL повинен починатися з https://"
        )

    return f"{base_url}{WEBHOOK_PATH}"


FREE_DAILY_TESTS: Final[int] = 3
EXPRESS_TEST_LENGTH: Final[int] = 5

REFERRAL_PREMIUM_DAYS: Final[int] = 3

PREMIUM_3_DAYS: Final[int] = 3
PREMIUM_30_DAYS: Final[int] = 30

STARS_3_DAYS: Final[int] = 49
STARS_30_DAYS: Final[int] = 199

RETENTION_CHECK_INTERVAL_SECONDS: Final[int] = 60 * 60
RETENTION_INACTIVE_HOURS: Final[int] = 24

DB_SEMAPHORE_LIMIT: Final[int] = 12
