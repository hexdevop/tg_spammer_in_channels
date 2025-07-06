from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select

from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from database import get_session
from database.models import Channel
from database.models.admin import Post
from variables import MediaType

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == "post"))
async def post_settings(
    event: types.CallbackQuery | types.Message,
    callback_data: ChannelsCallback,
    state: FSMContext,
    l10n: FluentLocalization,
):
    await state.clear()
    method = (
        event.message.edit_text
        if isinstance(event, types.CallbackQuery)
        else event.answer
    )
    async with get_session() as session:
        post = await session.scalar(
            select(Post).where(Post.channel_id == callback_data.id)
        )
        if post:
            channel = await session.scalar(
                select(Channel).where(Channel.id == callback_data.id)
            )
            await method(
                text=l10n.format_value(
                    "post-settings",
                    {
                        "mention": channel.mention,
                        "media_type": post.media_type.value,
                        "text": post.text or l10n.format_value("null"),
                        "keyboard": (
                            "✅" if post.reply_markup else l10n.format_value("null")
                        ),
                        "interval": post.interval,
                        "sent": post.sent,
                        "limit": post.limit,
                        "status": post.status.value,
                    },
                ),
                reply_markup=inline.post_settings(callback_data, post),
            )
        else:
            message_id = (
                await method(
                    text=l10n.format_value(
                        "add-the-post",
                        {"types": "\n".join([i.value for i in MediaType])},
                    ),
                    reply_markup=inline.cancel(callback_data, "settings"),
                )
            ).message_id
            await state.update_data(message_id=message_id)
            await state.update_data(callback_data=callback_data.model_dump())
            await state.set_state(ChannelState.post)
