from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, delete

from bot.handlers.admin.channel.settings import channel_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.utils import helper
from database import get_session
from database.models import Channel
from database.models.admin import Post

router = Router()


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
