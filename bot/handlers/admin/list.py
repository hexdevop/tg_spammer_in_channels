from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, func

from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from database import get_session
from database.models import Channel

router = Router()


@router.message(F.text == "Мои каналы 🔊")
async def my_channels_list(
    message: types.Message,
    state: FSMContext,
    l10n: FluentLocalization,
    page: int = 1,
    edit: bool = False,
):
    await state.clear()
    async with get_session() as session:
        channels = (
            await session.scalars(select(Channel).limit(16).offset((page - 1) * 16))
        ).all()
        count = await session.scalar(select(func.count(Channel.id)))
    method = message.edit_text if edit else message.answer
    await method(
        text=l10n.format_value("channels-list"),
        reply_markup=inline.channels_list(channels, page, count),
    )


@router.callback_query(ChannelsCallback.filter(F.action.in_({"main", "page"})))
async def main_and_pagination(
    call: types.CallbackQuery,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await my_channels_list(call.message, state, l10n, callback_data.page, edit=True)
