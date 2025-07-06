from aiogram import Dispatcher
from aiogram.enums import ChatType
from loguru import logger

from bot.filters.chat_type import ChatTypeFilter


def reg_routers(dp: Dispatcher):
    handlers = [
    ]
    for handler in handlers:
        handler.router.my_chat_member.filter(ChatTypeFilter(ChatType.CHANNEL))

        dp.include_router(handler.router)
    logger.opt(colors=True).info(
        f"<fg #aaf6ff>[channel {len(handlers)} handlers imported]</>"
    )
