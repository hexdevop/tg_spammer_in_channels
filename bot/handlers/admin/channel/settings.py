from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, func

from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from database import get_session
from database.models import Channel, Post

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "settings"))
async def channel_settings(
        event: types.CallbackQuery | types.Message,
        callback_data: ChannelsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    await state.clear()
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.id)
        )
        count = await session.scalar(
            select(func.count(Post.id)).where(Post.channel_id == callback_data.id)
        )
    method = event.message.edit_text if isinstance(event, types.CallbackQuery) else event.answer
    await method(
        text=channel.settings(l10n, count),
        reply_markup=inline.channel_settings(callback_data, channel),
    )
