import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from ..common.api import Api


class MainMiddleware(BaseMiddleware):
    api = None

    async def __call__(self, handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        if not self.api:
            self.api = Api(os.getenv('IP'), username=str(event.from_user.id), password=str(event.from_user.id))
        data['api'] = self.api
        return await handler(event, data)
