from aiogram import Dispatcher

from . import (
    admin,
    other,
)


def setup(dp: Dispatcher):
    admin.reg_routers(dp)
    other.reg_routers(dp)
