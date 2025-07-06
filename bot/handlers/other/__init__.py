from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from . import errors

from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [errors]
    for handler in handlers:
        handler.router.message.filter(ChatTypeFilter(ChatType.PRIVATE))

        dp.include_router(handler.router)
    logger.opt(colors=True).info(
        f"<fg #ffaaf1>[other {len(handlers)} handlers imported]</>"
    )
