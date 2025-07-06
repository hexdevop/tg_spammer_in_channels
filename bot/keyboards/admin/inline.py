from math import ceil

from bot.keyboards.admin.factory import ChannelsCallback
from bot.keyboards.utils import *
from database.models import Channel
from database.models.admin import Post
from variables import Status



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
            text=name,
            callback_data=data.pack()
        )
    sizes = generate_sizes([], channels, 2, 8, 1)
    data.action = 'add'
    builder.button(
        text='Добавить ➕',
        callback_data=data.pack()
    )
    sizes.append(1)
    return with_pagination(builder, data, ceil(count / 16), page, sizes)


def channel_settings(data: ChannelsCallback):
    builder = InlineKeyboardBuilder()
    data.action = 'post'
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
    return builder.adjust(1).as_markup()


def post_settings(data: ChannelsCallback, post: Post):
    builder = InlineKeyboardBuilder()
    sizes = []
    data.action = 'check'
    builder.button(
        text='Посмотреть пост 👀',
        callback_data=data.pack()
    )
    if post.status == Status.STOPPED:
        data.action = 'start'
        builder.button(
            text=f'Начать спам 🟢',
            callback_data=data.pack()
        )
    else:
        data.action = 'stop'
        builder.button(
            text='Остановить спам 🔴',
            callback_data=data.pack()
        )
    sizes.append(2)
    data.action = 'interval'
    builder.button(
        text='Интервал 🕓',
        callback_data=data.pack()
    )
    if post.limit == 0:
        data.action = 'set-limit'
        builder.button(
            text='Количество ☑️',
            callback_data=data.pack()
        )
        sizes.append(2)
    else:
        data.action = 'set-limit'
        builder.button(
            text='Количество ☑️',
            callback_data=data.pack()
        )
        data.action = 'off-limit'
        builder.button(
            text='Выключить лимит ⭕️',
            callback_data=data.pack()
        )
        sizes.append(1)
        sizes.append(2)
    data.action = 'delete-post'
    builder.button(
        text='Удалить 🗑',
        callback_data=data.pack()
    )
    sizes.append(1)
    data.action = 'settings'
    builder.button(
        text=back_text,
        callback_data=data.pack()
    )
    sizes.append(1)
    return builder.adjust(*sizes).as_markup()


def select_posting_type(data: ChannelsCallback):
    builder = InlineKeyboardBuilder()
    data.action = 'start-now'
    builder.button(
        text='📢 Начать сейчас',
        callback_data=data.pack()
    )
    data.action = 'start-later'
    builder.button(
        text='🕐 С интервалом',
        callback_data=data.pack()
    )
    data.action = 'post'
    builder.button(
        text=cancel_text,
        callback_data=data.pack()
    )
    return builder.adjust(2, 1).as_markup()
