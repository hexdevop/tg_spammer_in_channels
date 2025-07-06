from aiogram.fsm.state import StatesGroup, State


class ChannelState(StatesGroup):
    message_from_channel = State()
    post = State()
    interval = State()
    change_interval = State()
    limit = State()
