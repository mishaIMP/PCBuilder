import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from ..common.api import Api


class MainMiddleware(BaseMiddleware):
    api = None
    user_map = {}

    async def __call__(self, handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        if not self.api or user_id not in self.user_map:
            self.api = Api(os.getenv('IP'), username=str(user_id), password=str(user_id))
            self.user_map[user_id] = self.api.headers.get('Authorization')
        elif self.api.headers.get('Authorization') != self.user_map[user_id]:
            self.api.username = str(user_id)
            self.api.password = str(user_id)
            self.api.headers['Authorization'] = self.user_map[user_id]
        data['api'] = self.api
        return await handler(event, data)
