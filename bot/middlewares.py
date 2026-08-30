import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class AntiSpamMiddleware(BaseMiddleware):
    """
    Дуже легкий in-memory rate limiter.

    Не створює Redis-з'єднань і тому підходить для маленького
    Render instance.
    """

    def __init__(self, limit: float = 0.7) -> None:
        self.limit = limit
        self.last_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, Dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.monotonic()

        previous = self.last_time.get(user_id)

        if previous is not None and now - previous < self.limit:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Зачекайте секунду.",
                    show_alert=False,
                )

            return None

        self.last_time[user_id] = now

        # Не даємо словнику рости нескінченно.
        if len(self.last_time) > 10_000:
            cutoff = now - 60

            self.last_time = {
                uid: timestamp
                for uid, timestamp in self.last_time.items()
                if timestamp >= cutoff
            }

        return await handler(event, data)
