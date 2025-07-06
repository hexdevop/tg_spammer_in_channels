from aiogram import Dispatcher
from loguru import logger

from . import (
    main,
    add,
    interval,
    limit,
    other,
    start,
)
from bot.filters.admin import AdminFilter


def reg_routers(dp: Dispatcher):
    handlers = [
        main,
        add,
        interval,
        limit,
        other,
        start,
    ]
    for handler in handlers:
        handler.router.message.filter(AdminFilter())
        dp.include_router(handler.router)
    logger.opt(colors=True).info(
        f"<fg #ffb4aa>[admin.posts {len(handlers)} handlers imported]</>"
    )
