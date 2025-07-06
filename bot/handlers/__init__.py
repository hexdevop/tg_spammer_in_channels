from aiogram import Dispatcher

from . import (
    admin,
    channels,
    other,
)


def setup(dp: Dispatcher):
    channels.reg_routers(dp)
    admin.reg_routers(dp)
    other.reg_routers(dp)
