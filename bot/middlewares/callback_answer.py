from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


class CallbackAnswer(CallbackAnswerMiddleware):
    async def __call__(self, *args, **kwargs):
        try:
            await super().__call__(*args, **kwargs)
        except TelegramBadRequest:
            pass
