from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from bot.handlers.admin.posts.main import post_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from bot.utils import helper
from database import get_session
from database.models.admin import Post
from variables import MediaType

router = Router()


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
