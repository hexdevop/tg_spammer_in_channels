from aiogram import Dispatcher

from .callback_answer import CallbackAnswer


def setup(dp: Dispatcher):

    dp.callback_query.middleware(CallbackAnswer())
