from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, delete

from bot.handlers.admin.channel.list import my_channels_list
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from database import get_session
from database.models import Channel, Post

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == 'delete'))
async def delete_channel(
        call: types.CallbackQuery,
        callback_data: ChannelsCallback,
        l10n: FluentLocalization,
):
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.id)
        )
    await call.message.edit_text(
        text=l10n.format_value('confirm-deleting-channel', {'mention': channel.mention}),
        reply_markup=inline.confirm(callback_data, 'confirm-deleting', 'settings')
    )


@router.callback_query(ChannelsCallback.filter(F.action == 'confirm-deleting'))
async def confirm_deleting_channel(
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
            await session.execute(
                delete(Channel).where(Channel.id == callback_data.id)
            )
    await my_channels_list(call.message, state, l10n, callback_data.page, edit=True)
