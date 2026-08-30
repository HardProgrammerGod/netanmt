import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class AntiSpamMiddleware(BaseMiddleware):
    """
    Lightweight anti-spam protection.

    Keeps memory bounded so the Render free instance does not
    accumulate unlimited user IDs.
    """

    def __init__(
        self,
        limit: float = 0.7,
        max_users: int = 5000,
    ):
        self.limit = limit
        self.max_users = max_users
        self.last_time: OrderedDict[int, float] = OrderedDict()

    async def __call__(
        self,
        handler: Callable[
            [Any, dict],
            Awaitable[Any],
        ],
        event: Any,
        data: dict,
    ) -> Any:

        if not isinstance(
            event,
            (Message, CallbackQuery),
        ):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        current_time = time.monotonic()

        last_time = self.last_time.get(user_id)

        if (
            last_time is not None
            and current_time - last_time < self.limit
        ):
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Зачекай секунду.",
                    show_alert=False,
                )

            return None

        self.last_time[user_id] = current_time
        self.last_time.move_to_end(user_id)

        if len(self.last_time) > self.max_users:
            self.last_time.popitem(last=False)

        return await handler(event, data)
