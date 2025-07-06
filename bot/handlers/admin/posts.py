from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, update, case, delete

from bot.handlers.admin.list import my_channels_list
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from database import get_session
from database.models import Channel
from variables import Status

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "posts"))
async def posts_list(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.id)
        )
    await call.message.edit_text(
        text=channel.settings(l10n),
        reply_markup=inline.channel_settings(callback_data, channel),
    )
