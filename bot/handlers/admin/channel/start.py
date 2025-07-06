from aiogram import types, Router, F
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent.runtime import FluentLocalization
from sqlalchemy import select, update

from bot.handlers.admin.channel.settings import channel_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.utils import helper
from database import get_session
from database.models import Channel, Post
from variables import Status

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "start"))
async def start_posting(
        call: types.CallbackQuery,
        callback_data: ChannelsCallback,
        l10n: FluentLocalization,
):
    await call.message.edit_text(
        text=l10n.format_value("select-spamming-type"),
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

    try:
        async with get_session() as session, session.begin():
            channel = await session.scalar(
                select(Channel).where(Channel.id == callback_data.id)
            )
            number = (channel.last_posted_number or 0) + 1
            post = await session.scalar(
                select(Post).where(
                    Post.channel_id == channel.id,
                    Post.number == number
                )
            )
            if not post:
                post = await session.scalar(
                    select(Post).where(
                        Post.channel_id == channel.id,
                        Post.number == 1
                    )
                )
                channel.sent += 1

            if not post:
                return await call.answer(
                    text=l10n.format_value('no-post-found'),
                    show_alert=True,
                )

            if not later:
                message = await helper.send_post(call.bot, post, channel.chat_id)
                channel.last_message_id = message.message_id
                channel.last_posted_number = post.number

            channel.status = Status.WORKING

        job_id = f"spam:{channel.chat_id}"
        job = scheduler.get_job(job_id)
        if job:
            job.remove()
        scheduler.add_job(
            id=job_id,
            func=helper.spamming,
            trigger="interval",
            seconds=channel.interval,
            kwargs={"chat_id": channel.chat_id},
        )

        return await channel_settings(call, callback_data, state, l10n)

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
            chat_id = await session.scalar(
                select(Channel.chat_id).where(Channel.id == callback_data.id)
            )
            await session.execute(
                update(Channel).where(Channel.id == callback_data.id)
                .values(status=Status.STOPPED)
            )
    job = scheduler.get_job(f"spam:{chat_id}")
    if job:
        job.remove()
    return await channel_settings(call, callback_data, state, l10n)
