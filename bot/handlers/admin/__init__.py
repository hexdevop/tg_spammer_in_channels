from aiogram import Dispatcher

from . import (
    channel,
    posts,
    unhandled,
    start,
)
from bot.filters.admin import AdminFilter


def reg_routers(dp: Dispatcher):
    start.router.message.filter(AdminFilter())
    dp.include_router(start.router)

    channel.reg_routers(dp)
    posts.reg_routers(dp)

    unhandled.router.message.filter(AdminFilter())
    dp.include_router(unhandled.router)
