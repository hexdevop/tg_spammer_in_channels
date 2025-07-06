from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent.runtime import FluentLocalization
from sqlalchemy import select, update

from bot.handlers.admin.posts.main import post_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from bot.utils import helper
from database import get_session
from database.models import Channel
from database.models.admin import Post

router = Router()


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
