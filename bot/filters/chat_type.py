from typing import Union

from aiogram import types
from aiogram.filters import BaseFilter


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, event: types.Message | types.CallbackQuery) -> bool:
        chat = event.message.chat if isinstance(event, types.CallbackQuery) else event.chat
        if isinstance(self.chat_type, str):
            return chat.type == self.chat_type
        else:
            return chat.type in self.chat_type
