from aiogram import types, Router, F
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent.runtime import FluentLocalization
from sqlalchemy import select

from bot.handlers.admin.posts.main import post_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.utils import helper
from database import get_session
from database.models import Channel
from database.models.admin import Post
from variables import Status

router = Router()


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
    try:
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
        job = scheduler.get_job(f"spam:{chat_id}")
        if job:
            job.remove()
        scheduler.add_job(
            id=f"spam:{chat_id}",
            func=helper.spamming,
            trigger="interval",
            seconds=post.interval,
            kwargs={"chat_id": chat_id, "post_id": post.id},
        )
        return await post_settings(call, callback_data, state, l10n)
    except TelegramForbiddenError:
        text = l10n.format_value('bot-is-a-not-member-of-the-channel')
    except TelegramBadRequest:
        text = l10n.format_value('bot-dont-have-enough-rights')
    await call.message.edit_text(text=text)


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
