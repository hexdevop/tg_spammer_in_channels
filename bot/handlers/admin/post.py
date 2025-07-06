import datetime

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent.runtime import FluentLocalization
from sqlalchemy import select, delete, update

from bot.handlers.admin.settings import channel_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from bot.utils import helper
from database import get_session
from database.models import Channel
from database.models.admin import Post
from variables import MediaType, Status

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "post"))
async def post_settings(
    event: types.CallbackQuery | types.Message,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    method = (
        event.message.edit_text
        if isinstance(event, types.CallbackQuery)
        else event.answer
    )
    async with get_session() as session:
        post = await session.scalar(
            select(Post).where(Post.channel_id == callback_data.id)
        )
        if post:
            channel = await session.scalar(
                select(Channel).where(Channel.id == callback_data.id)
            )
            await method(
                text=l10n.format_value(
                    "post-settings",
                    {
                        "mention": channel.mention,
                        "media_type": post.media_type.value,
                        "text": post.text or l10n.format_value("null"),
                        "keyboard": (
                            "✅" if post.reply_markup else l10n.format_value("null")
                        ),
                        "interval": post.interval,
                        "sent": post.sent,
                        "limit": post.limit,
                        "status": post.status.value,
                    },
                ),
                reply_markup=inline.post_settings(callback_data, post),
            )
        else:
            message_id = (
                await method(
                    text=l10n.format_value(
                        "add-the-post",
                        {"types": "\n".join([i.value for i in MediaType])},
                    ),
                    reply_markup=inline.cancel(callback_data, "settings"),
                )
            ).message_id
            await state.update_data(message_id=message_id)
            await state.update_data(callback_data=callback_data.model_dump())
            await state.set_state(ChannelState.post)


@router.message(ChannelState.post)
async def get_the_post(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = ChannelsCallback.model_validate(data.get("callback_data"))
    try:
        media_type: MediaType = getattr(MediaType, message.content_type.upper())
        if media_type is MediaType.TEXT:
            file_id = None
        else:
            if media_type is MediaType.PHOTO:
                file_id = message.photo[-1].file_id
            else:
                file_id = getattr(message, message.content_type).file_id
        message_id = (
            await message.answer(
                text=l10n.format_value("get-post-interval"),
                reply_markup=inline.cancel(callback_data, "main"),
            )
        ).message_id
        await state.update_data(
            message_id=message_id,
            media_type=media_type.name.upper(),
            file_id=file_id,
            text=message.html_text,
            reply_markup=(
                message.reply_markup.model_dump() if message.reply_markup else None
            ),
        )
        await state.set_state(ChannelState.interval)
    except AttributeError:
        message_id = (
            await message.answer(
                text=l10n.format_value(
                    "unsupported-post-type",
                    {"types": "\n".join([i.value for i in MediaType])},
                ),
                reply_markup=inline.cancel(callback_data, "main"),
            )
        ).message_id
        await state.update_data(message_id=message_id)


@router.message(ChannelState.interval, F.text)
async def get_interval(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = ChannelsCallback.model_validate(data.get("callback_data"))
    if message.text.isdigit():
        async with get_session() as session:
            async with session.begin():
                session.add(
                    Post(
                        channel_id=callback_data.id,
                        media_type=data.get("media_type"),
                        media=data.get("file_id"),
                        text=data.get("text"),
                        reply_markup=data.get("reply_markup"),
                        interval=int(message.text),
                    )
                )

        await message.answer(text=l10n.format_value("post-add-successfully"))
        await post_settings(message, callback_data, state, l10n)
    else:
        message_id = (
            await message.answer(
                text=l10n.format_value("its-not-digit"),
                reply_markup=inline.cancel(callback_data, "main"),
            )
        ).message_id
        await state.update_data(message_id=message_id)


@router.callback_query(ChannelsCallback.filter(F.action == "check"))
async def check_post(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
):
    async with get_session() as session:
        post = await session.scalar(
            select(Post).where(Post.channel_id == callback_data.id)
        )
    await helper.send_post(call.bot, post, call.from_user.id)


@router.callback_query(ChannelsCallback.filter(F.action == "interval"))
async def set_other_interval(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    message_id = (
        await call.message.edit_text(
            text=l10n.format_value("get-post-interval"),
            reply_markup=inline.cancel(callback_data, "post"),
        )
    ).message_id
    await state.update_data(
        message_id=message_id, callback_data=callback_data.model_dump()
    )
    await state.set_state(ChannelState.change_interval)


@router.message(ChannelState.change_interval, F.text)
async def get_other_interval(
    message: types.Message,
    scheduler: AsyncIOScheduler,
    state: FSMContext,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = ChannelsCallback.model_validate(data.get("callback_data"))
    if message.text.isdigit():
        interval = int(message.text)
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    update(Post)
                    .where(Post.channel_id == callback_data.id)
                    .values(interval=interval)
                )
                chat_id, post_id = (await session.execute(
                    select(Channel.chat_id, Post.id)
                    .join(Post, Channel.id == Post.channel_id)
                    .where(Channel.id == callback_data.id)
                )).fetchone()
        job = scheduler.get_job(f"spam:{chat_id}")
        if job:
            job.remove()
        scheduler.add_job(
            id=f"spam:{chat_id}",
            func=helper.spamming,
            trigger="interval",
            seconds=interval,
            kwargs={"chat_id": chat_id, "post_id": post_id},
        )
        await post_settings(message, callback_data, state, l10n)
    else:
        message_id = (
            await message.answer(
                text=l10n.format_value("its-not-digit"),
                reply_markup=inline.cancel(callback_data, "post"),
            )
        ).message_id
        await state.update_data(message_id=message_id)


@router.callback_query(ChannelsCallback.filter(F.action == "set-limit"))
async def set_limit(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    message_id = (
        await call.message.edit_text(
            text=l10n.format_value("get-post-limit"),
            reply_markup=inline.cancel(callback_data, "post"),
        )
    ).message_id
    await state.update_data(
        message_id=message_id, callback_data=callback_data.model_dump()
    )
    await state.set_state(ChannelState.limit)


@router.message(ChannelState.limit, F.text)
async def get_limit(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = ChannelsCallback.model_validate(data.get("callback_data"))
    if message.text.isdigit():
        async with get_session() as session:
            async with session.begin():
                await session.execute(
                    update(Post)
                    .where(Post.channel_id == callback_data.id)
                    .values(limit=int(message.text))
                )
        await post_settings(message, callback_data, state, l10n)
    else:
        message_id = (
            await message.answer(
                text=l10n.format_value("its-not-digit"),
                reply_markup=inline.cancel(callback_data, "post"),
            )
        ).message_id
        await state.update_data(message_id=message_id)


@router.callback_query(ChannelsCallback.filter(F.action == "off-limit"))
async def off_limit(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            await session.execute(
                update(Post).where(Post.channel_id == callback_data.id).values(limit=0)
            )
    await post_settings(call, callback_data, state, l10n)


@router.callback_query(ChannelsCallback.filter(F.action == "delete-post"))
async def delete_post(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    l10n: FluentLocalization,
):
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.id)
        )
    await call.message.edit_text(
        text=l10n.format_value("confirm-deleting-post", {"mention": channel.mention}),
        reply_markup=inline.confirm(callback_data, "confirm-deleting-post", "post"),
    )


@router.callback_query(ChannelsCallback.filter(F.action == "confirm-deleting-post"))
async def confirm_deleting_post(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            await session.execute(
                delete(Post).where(Post.channel_id == callback_data.id)
            )
    await channel_settings(call, callback_data, state, l10n)


@router.callback_query(ChannelsCallback.filter(F.action == "start"))
async def start_posting(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    l10n: FluentLocalization,
):
    await call.message.edit_text(
        text=l10n.format_value("select-posting-type"),
        reply_markup=inline.select_posting_type(callback_data),
    )


@router.callback_query(ChannelsCallback.filter(F.action.startswith('start-')))
async def start_now(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    scheduler: AsyncIOScheduler,
    state: FSMContext,
    l10n: FluentLocalization,
):
    later = callback_data.action.endswith('later')
    async with get_session() as session:
        async with session.begin():
            post = await session.scalar(
                select(Post).where(Post.channel_id == callback_data.id)
            )
            chat_id = await session.scalar(
                select(Channel.chat_id).where(Channel.id == callback_data.id)
            )
            if not later:
                message = await helper.send_post(call.bot, post, chat_id)
                post.sent += 1
                post.last_message_id = message.message_id
            post.status = Status.WORKING
    scheduler.add_job(
        id=f"spam:{chat_id}",
        func=helper.spamming,
        trigger="interval",
        seconds=post.interval,
        kwargs={"chat_id": chat_id, "post_id": post.id},
    )
    await post_settings(call, callback_data, state, l10n)


@router.callback_query(ChannelsCallback.filter(F.action == "stop"))
async def stop_spamming(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    scheduler: AsyncIOScheduler,
    state: FSMContext,
    l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            post = await session.scalar(
                select(Post).where(Post.channel_id == callback_data.id)
            )
            chat_id = await session.scalar(
                select(Channel.chat_id).where(Channel.id == callback_data.id)
            )
            post.status = Status.STOPPED
    job = scheduler.get_job(f"spam:{chat_id}")
    if job:
        job.remove()
    await post_settings(call, callback_data, state, l10n)
