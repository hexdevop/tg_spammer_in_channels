from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization
from sqlalchemy import select, func

from bot.keyboards.admin import inline
from bot.keyboards.admin.factory import ChannelsCallback, PostsCallback
from database import get_session
from database.models import Channel, Post

router = Router()


@router.callback_query(ChannelsCallback.filter(F.action == 'posts'))
async def posts_list(
        event: types.CallbackQuery | types.Message,
        callback_data: ChannelsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
        page: int = 1,
        edit: bool = True,
):
    await state.clear()
    async with get_session() as session:
        channel = await session.scalar(
            select(Channel).where(Channel.id == callback_data.id)
        )
        posts = (await session.scalars(
            select(Post).where(Post.channel_id == callback_data.id)
            .order_by(Post.number.asc())
            .limit(8).offset((page - 1) * 8)
        )).all()
        count = await session.scalar(
            select(func.count(Post.id)).where(Post.channel_id == callback_data.id)
        )
    message = event if isinstance(event, types.Message) else event.message
    method = message.edit_text if edit else message.answer
    await method(
        text=l10n.format_value('posts-list', {'mention': channel.mention}),
        reply_markup=inline.posts_list(callback_data, posts, page, count)
    )


@router.callback_query(PostsCallback.filter(F.action.in_({'list', 'page'})))
async def back_to_list__and__pagination(
        event: types.CallbackQuery | types.Message,
        callback_data: PostsCallback,
        state: FSMContext,
        l10n: FluentLocalization,
):
    data = ChannelsCallback(action=callback_data.action, id=callback_data.channel_id, page=callback_data.channel_page)
    await posts_list(event, data, state, l10n, callback_data.page, edit=isinstance(event, types.CallbackQuery))
