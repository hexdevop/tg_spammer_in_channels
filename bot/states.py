from aiogram.fsm.state import StatesGroup, State


class ChannelState(StatesGroup):
    message_from_channel = State()

    interval = State()
    limit = State()


class PostState(StatesGroup):
    post = State()
