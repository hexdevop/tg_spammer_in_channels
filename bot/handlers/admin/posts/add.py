from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select

from bot.handlers.admin.posts.list import back_to_list__and__pagination
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import PostsCallback
from bot.states import PostState
from bot.utils import helper
from database import get_session
from database.models import Post
from variables import MediaType

router = Router()


@router.callback_query(PostsCallback.filter(F.action == 'add'))
async def add_post(
        call: types.CallbackQuery,
        callback_data: PostsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    await state.clear()
    message_id = (
        await call.message.edit_text(
            text=l10n.format_value(
                "add-the-post",
                {"types": "\n".join([i.value for i in MediaType])},
            ),
            reply_markup=inline.cancel(callback_data, "list"),
        )
    ).message_id
    await state.update_data(message_id=message_id)
    await state.update_data(callback_data=callback_data.model_dump())
    await state.set_state(PostState.post)


@router.message(PostState.post)
async def get_the_post(
        message: types.Message,
        state: FSMContext,
        l10n: FluentLocalization,
):
    data = await state.get_data()
    await helper.delete_messages(message, data)
    callback_data = PostsCallback.model_validate(data.get("callback_data"))
    try:
        media_type: MediaType = getattr(MediaType, message.content_type.upper())
        if media_type is MediaType.TEXT:
            file_id = None
        else:
            if media_type is MediaType.PHOTO:
                file_id = message.photo[-1].file_id
            else:
                file_id = getattr(message, message.content_type).file_id
        async with get_session() as session:
            async with session.begin():
                last_number = await session.scalar(
                    select(Post.number).order_by(Post.number.desc()).limit(1)
                )
                session.add(
                    Post(
                        channel_id=callback_data.channel_id,
                        number=last_number + 1 if last_number else 1,
                        media_type=media_type,
                        media=file_id,
                        text=message.html_text,
                        reply_markup=message.reply_markup.model_dump() if message.reply_markup else None,
                    )
                )
        await message.answer(text=l10n.format_value("post-add-successfully"))
        await back_to_list__and__pagination(message, callback_data, state, l10n)
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


