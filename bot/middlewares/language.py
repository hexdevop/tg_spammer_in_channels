from typing import Dict, Any, Awaitable, Callable, Union
from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.services import Cache


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Union[Update, Any],
        data: Dict[str, Any],
    ) -> Any:
        try:
            chat = data["event_chat"]
            cache: Cache = data["cache"]
            lang = await cache.get_language(chat.id, lang_only=True)
            data['lang'] = lang
            data["l10n"] = cache.get_l10n(lang)
        except KeyError:
            pass
        return await handler(event, data)