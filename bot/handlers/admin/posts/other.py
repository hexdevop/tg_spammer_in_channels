from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, delete, update

from bot.handlers.admin.posts.list import back_to_list__and__pagination
from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import PostsCallback
from bot.utils import helper
from database import get_session
from database.models import Post, Channel

router = Router()


@router.callback_query(PostsCallback.filter(F.action == "up"))
async def up_post(
        call: types.CallbackQuery,
        callback_data: PostsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            current_number = await session.scalar(
                select(Post.number).where(Post.id == callback_data.id)
            )
            upper_number = await session.scalar(
                select(Post.number)
                .where(
                    Post.channel_id == callback_data.channel_id,
                    Post.number == current_number - 1
                )
            )
            if upper_number:
                await session.execute(
                    update(Post)
                    .where(
                        Post.channel_id == callback_data.channel_id,
                        Post.number == upper_number
                    )
                    .values(number=Post.number + 1)
                )
                await session.execute(
                    update(Post).where(Post.id == callback_data.id)
                    .values(number=Post.number - 1)
                )
    await back_to_list__and__pagination(call, callback_data, state, l10n)


@router.callback_query(PostsCallback.filter(F.action == "show"))
async def show_post(
        call: types.CallbackQuery,
        callback_data: PostsCallback,
):
    async with get_session() as session:
        post = await session.scalar(
            select(Post).where(Post.id == callback_data.id)
        )
    await helper.send_post(call.bot, post, call.from_user.id)


@router.callback_query(PostsCallback.filter(F.action == "delete"))
async def delete_post(
        call: types.CallbackQuery,
        callback_data: PostsCallback,
        l10n: FluentLocalization,
):
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.channel_id)
        )
    await call.message.edit_text(
        text=l10n.format_value("confirm-deleting-post", {"mention": channel.mention}),
        reply_markup=inline.confirm(callback_data, "confirm-deleting", "post"),
    )


@router.callback_query(PostsCallback.filter(F.action == "confirm-deleting"))
async def confirm_deleting_post(
        call: types.CallbackQuery,
        callback_data: PostsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    async with get_session() as session:
        async with session.begin():
            number = await session.scalar(
                select(Post.number).where(Post.id == callback_data.id)
            )
            await session.execute(
                delete(Post).where(Post.id == callback_data.id)
            )
            await session.execute(
                update(Post)
                .where(
                    Post.channel_id == callback_data.channel_id,
                    Post.number > number
                )
                .values(number=Post.number - 1)
            )
    await back_to_list__and__pagination(call, callback_data, state, l10n)
