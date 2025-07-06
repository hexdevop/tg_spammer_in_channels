from aiogram import types, exceptions, Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent.runtime import FluentLocalization
from sqlalchemy import select

from database import get_session
from database.models import Channel
from database.models.admin import Post
from variables import MediaType, Status, variables


async def delete_messages(
        event: types.Message | types.CallbackQuery, data: dict = None, user_id: int = None
):
    try:
        if isinstance(event, types.Message):
            message_ids = [event.message_id]
        else:
            message_ids = [event.message.message_id]
        if data:
            message_ids += data.get("message_ids", [])
            if "message_id" in data.keys():
                message_ids.append(data.get("message_id"))
        await event.bot.delete_messages(
            chat_id=user_id or event.from_user.id, message_ids=message_ids
        )
    except exceptions.TelegramBadRequest:
        pass


async def delete_message(bot: Bot, user_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id=user_id, message_id=message_id)
    except exceptions.TelegramBadRequest:
        pass


async def send_post(
    bot: Bot,
    post: Post,
    chat_id: int,
):
    if post.media_type == MediaType.TEXT:
        return await bot.send_message(
            chat_id=chat_id,
            text=post.text,
            reply_markup=post.reply_markup,
        )

    media_attr = post.media_type.name.lower()
    send_method = getattr(bot, f"send_{media_attr}", None)
    if not send_method:
        raise ValueError(f"Unsupported media type: {post.media_type}")

    params = {
        "chat_id": chat_id,
        media_attr: post.media,
        "reply_markup": post.reply_markup,
    }

    if post.media_type not in [MediaType.VIDEO_NOTE, MediaType.STICKER]:
        params["caption"] = post.text

    return await send_method(**params)



async def spamming(bot: Bot, scheduler: AsyncIOScheduler, l10n: FluentLocalization, chat_id: int, post_id: int):
    async with get_session() as session:
        async with session.begin():
            post = await session.scalar(select(Post).where(Post.id == post_id))
            if not post:
                return

            job = scheduler.get_job(f"spam:{chat_id}")

            try:
                if post.status == Status.WORKING and (post.limit == 0 or post.sent < post.limit):
                    if post.last_message_id:
                        await delete_message(bot, chat_id, post.last_message_id)

                    message = await send_post(bot, post, chat_id)
                    post.last_message_id = message.message_id
                    post.sent += 1
                else:
                    if job:
                        job.remove()
                    post.status = Status.STOPPED
                return

            except (TelegramForbiddenError, TelegramBadRequest) as e:
                if isinstance(e, TelegramForbiddenError):
                    text = l10n.format_value('bot-is-a-not-member-of-the-channel')
                else:
                    text = l10n.format_value('bot-dont-have-enough-rights')

                if job:
                    job.remove()
                post.status = Status.STOPPED

                channel = await session.scalar(
                    select(Channel).where(Channel.chat_id == chat_id)
                )

                for admin_id in variables.admins:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=l10n.format_value('bot-caught-error', {'mention': channel.mention})
                    )
                    await bot.send_message(chat_id=admin_id, text=text)
