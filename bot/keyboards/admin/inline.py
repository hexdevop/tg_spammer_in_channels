from math import ceil

from bot.keyboards.admin.factory import ChannelsCallback, PostsCallback
from bot.keyboards.utils import *
from database.models import Channel, Post
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


def channel_settings(data: ChannelsCallback, channel: Channel):
    builder = InlineKeyboardBuilder()
    sizes = []
    if channel.status == Status.STOPPED:
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
    sizes.append(1)
    data.action = 'interval'
    builder.button(
        text='Интервал 🕓',
        callback_data=data.pack()
    )
    if channel.limit == 0:
        data.action = 'set-limit'
        builder.button(
            text='Установить круги ☑️',
            callback_data=data.pack()
        )
        sizes.append(2)
    else:
        data.action = 'set-limit'
        builder.button(
            text='Изменить круги ☑️',
            callback_data=data.pack()
        )
        data.action = 'off-limit'
        builder.button(
            text='Бесконечные круги ♾️',
            callback_data=data.pack()
        )
        sizes.append(1)
        sizes.append(2)
    data.action = 'delete'
    builder.button(
        text='Удалить 🗑',
        callback_data=data.pack()
    )
    data.action = 'posts'
    builder.button(
        text='Посты 💬 ',
        callback_data=data.pack()
    )
    sizes.append(2)
    data.action = 'list'
    builder.button(
        text=back_text,
        callback_data=data.pack()
    )
    sizes.append(1)
    return builder.adjust(*sizes).as_markup()


def posts_list(channel_data: ChannelsCallback, posts: List[Post], page: int, count: int):
    builder = InlineKeyboardBuilder()
    data = PostsCallback(action='settings', page=page, channel_id=channel_data.id, channel_page=channel_data.page)
    sizes = []
    for post in posts:
        data.id = post.id
        data.action = 'up'
        builder.button(
            text=f"⬆️ #{post.number}",
            callback_data=data.pack()
        )
        data.action = 'show'
        builder.button(
            text=f"👀 Пост {post.id}",
            callback_data=data.pack()
        )
        data.action = 'delete'
        builder.button(
            text=f"Удалить 🗑",
            callback_data=data.pack()
        )
    if posts:
        sizes += [3] * len(posts)
    data.action = 'add'
    builder.button(
        text='Добавить ➕',
        callback_data=data.pack()
    )
    sizes.append(1)
    builder, sizes = with_pagination(builder, data, ceil(count / 8), page, sizes, as_markup=False)
    channel_data.action = 'settings'
    builder.button(
        text=back_text,
        callback_data=channel_data.pack()
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
    data.action = 'settings'
    builder.button(
        text=cancel_text,
        callback_data=data.pack()
    )
    return builder.adjust(2, 1).as_markup()
