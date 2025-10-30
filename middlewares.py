from collections.abc import Awaitable, Callable
import logging
from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)

class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_list: list[int]) -> None:
        super().__init__()
        self.admin_list = admin_list
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        if event.from_user.id in self.admin_list:
            return await handler(event, data)
        
        logger.info(f"Unathorized user access attempt: {event.from_user}")
        