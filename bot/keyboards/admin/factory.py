from aiogram.filters.callback_data import CallbackData


class ChannelsCallback(CallbackData, prefix='channel'):
    action: str
    id: int = 0
    page: int


class PostsCallback(CallbackData, prefix='posts'):
    action: str

    id: int = 0
    page: int

    channel_id: int
    channel_page: int