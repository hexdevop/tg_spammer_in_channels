import traceback

from aiogram import types, Router, html
from aiogram.exceptions import TelegramBadRequest

from config import config
from variables import variables

router = Router()


@router.errors()
async def error_handler(event: types.ErrorEvent):
    if config.bot.error_notification != 0:
        exception_class = event.exception.__class__

        # if exception_class not in [TelegramBadRequest, DataError]:
        #     raise event.exception
        #     return

        bot = event.update.bot
        error_traceback = traceback.format_exc().encode("utf-8")
        file = types.BufferedInputFile(error_traceback, filename="error.txt")

        chat_ids = variables.admins if config.bot.error_notification == 1 else [491264374]
        event_ = getattr(event.update, event.update.event_type)
        postfix = f"\n\nОшибка от пользователя <code>{event_.from_user.id}</>"
        for chat_id in chat_ids:
            try:
                await bot.send_document(
                    chat_id=chat_id,
                    document=file,
                    caption=f"<code>{html.quote(str(exception_class))}: {html.quote(str(event.exception))}</>{postfix}",
                )
            except TelegramBadRequest:
                await bot.send_document(
                    chat_id=chat_id,
                    document=file,
                    caption=f"<code>{html.quote(str(exception_class))}</>{postfix}",
                )
