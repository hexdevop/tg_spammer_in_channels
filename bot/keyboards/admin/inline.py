from math import ceil

from bot.keyboards.admin.factory import ChannelsCallback
from bot.keyboards.utils import *
from database.models import Channel
from variables import Status, MediaType



def channels_list(channels: List[Channel], page: int, count: int):
    builder = InlineKeyboardBuilder()
    data = ChannelsCallback(action='settings', page=page)
    for channel in channels:
        data.id = channel.id
        name = (
            (channel.title[:25] + "...")
            if len(channel.title) > 25
            else channel.title
        )
        builder.button(
            text=f"{name} | {"🟢" if channel.status == Status.WORKING else "🔴"}",
            callback_data=data.pack()
        )
    data.action = 'add'
    builder.button(
        text='Добавить ➕',
        callback_data=data.pack()
    )
    sizes = [1] * 8 + [1]
    return with_pagination(builder, data, ceil(count / 8), page, sizes)


def channel_settings(data: ChannelsCallback, channel: Channel):
    builder = InlineKeyboardBuilder()
    data.action = 'status'
    builder.button(
        text=f'Статус - {"🟢" if channel.status == Status.WORKING else "🔴"}',
        callback_data=data.pack()
    )
    data.action = 'posts'
    builder.button(
        text='Пост 💬 ',
        callback_data=data.pack()
    )
    data.action = 'delete'
    builder.button(
        text='Удалить 🗑',
        callback_data=data.pack()
    )
    data.action = 'main'
    builder.button(
        text=back_text,
        callback_data=data.pack()
    )
    return builder.adjust(2, 1, 1).as_markup()
