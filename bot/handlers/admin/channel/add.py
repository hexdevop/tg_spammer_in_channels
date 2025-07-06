from aiogram import types, Router, F
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from bot.handlers.admin.channel.list import my_channels_list
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from bot.utils import helper
from database import get_session
from database.models import Channel

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "add"))
async def add_channel(
        call: types.CallbackQuery,
        callback_data: ChannelsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    await state.clear()
    message_id = (
        await call.message.edit_text(
            text=l10n.format_value("forward-me-message-from-channel"),
            reply_markup=inline.cancel(callback_data, "list"),
        )
    ).message_id
    await state.update_data(message_id=message_id)
    await state.update_data(callback_data=callback_data.model_dump())
    await state.set_state(ChannelState.message_from_channel)


@router.message(ChannelState.message_from_channel)
async def forwarded_message(
        message: types.Message,
        state: FSMContext,
        l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = ChannelsCallback.model_validate(data.get("callback_data"))
    text = "forward-me-message-from-channel"
    if message.forward_from_chat:
        channel = message.forward_from_chat
        try:
            member = await message.bot.get_chat_member(channel.id, message.bot.id)
            if (
                    member.status == ChatMemberStatus.ADMINISTRATOR
                    and member.can_post_messages
                    and member.can_delete_messages
            ):
                async with get_session() as session:
                    async with session.begin():
                        channel = Channel(
                            chat_id=channel.id,
                            title=channel.title,
                            username=channel.username,
                        )
                        session.add(channel)
                await message.answer(
                    text=l10n.format_value(
                        "channel-successfully-add", {"mention": channel.mention}
                    )
                )
                return await my_channels_list(message, state, l10n, callback_data.page)
            else:
                text = "bot-dont-have-enough-rights"
        except TelegramForbiddenError:
            text = "bot-is-a-not-member-of-the-channel"
    message_id = (
        await message.answer(
            text=l10n.format_value(text),
            reply_markup=inline.cancel(callback_data, "main"),
        )
    ).message_id
    await state.update_data(message_id=message_id)
