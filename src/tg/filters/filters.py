"""
Кастомный фильтр, который проверяет, есть ли в БД такой посетитель.
Если нет - в роутере auth проводим его авторизацию.
"""

from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from service_layer.service import should_auth


class NotAuthFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        return await should_auth(message.from_user.id)
