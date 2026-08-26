import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.7):
        self.limit = limit
        self.last_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.last_time and (current_time - self.last_time[user_id]) < self.limit:
            if isinstance(event, CallbackQuery):
                await event.answer("Зачекайте секунду перед наступним кліком!", show_alert=False)
            return

        self.last_time[user_id] = current_time
        return await handler(event, data)
