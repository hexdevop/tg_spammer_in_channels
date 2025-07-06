from aiogram import Dispatcher
from loguru import logger

from . import (
    list,
    add,
    other,
)
from bot.filters.admin import AdminFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        list,
        add,
        other,
    ]
    for handler in handlers:
        handler.router.message.filter(AdminFilter())
        dp.include_router(handler.router)
    logger.opt(colors=True).info(
        f"<fg #ffb4aa>[admin.posts {len(handlers)} handlers imported]</>"
    )
