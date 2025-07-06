from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, update

from bot.handlers.admin.posts.main import post_settings
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback
from bot.states import ChannelState
from bot.utils import helper
from database import get_session
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


@router.callback_query(ChannelsCallback.filter(F.action == "set-limit"))
async def set_limit(
        call: types.CallbackQuery,
        callback_data: ChannelsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    await state.clear()
    message_id = (
        await call.message.edit_text(
            text=l10n.format_value("get-post-limit"),
            reply_markup=inline.cancel(callback_data, "post"),
        )
    ).message_id
    await state.update_data(
        message_id=message_id, callback_data=callback_data.model_dump()
    )
    await state.set_state(ChannelState.limit)


@router.message(ChannelState.limit, F.text)
async def get_limit(
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
                await session.execute(
                    update(Post)
                    .where(Post.channel_id == callback_data.id)
                    .values(limit=int(message.text))
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


@router.callback_query(ChannelsCallback.filter(F.action == "off-limit"))
async def off_limit(
        call: types.CallbackQuery,
        callback_data: ChannelsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            await session.execute(
                update(Post).where(Post.channel_id == callback_data.id).values(limit=0)
            )
    await post_settings(call, callback_data, state, l10n)
