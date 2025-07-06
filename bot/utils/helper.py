import re
import string
import random
from aiogram import types, exceptions, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from database import get_session
from database.models.admin import Post
from variables import MediaType, Status


def get_percent(all_count: int, count: int) -> int:
    return round((count / all_count) * 100) if all_count else 0


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


def generate_symbols(length: int = 7, use_numbers: bool = True):
    characters = (
        string.ascii_letters + string.digits if use_numbers else string.ascii_letters
    )
    return "".join(random.choice(characters) for _ in range(length))


def has_cyrillic(text):
    return bool(re.search("[а-яА-Я]", text))


async def send_post(
    bot: Bot,
    post: Post,
    chat_id: int,
):
    if post.media_type == MediaType.TEXT:
        await bot.send_message(
            chat_id=chat_id,
            text=post.text,
            reply_markup=post.reply_markup,
        )
    else:
        method = getattr(bot, f"send_{post.media_type.name.lower()}")
        params = {
            "chat_id": chat_id,
            post.media_type.name.lower(): post.media,
            "caption": post.text,
            "reply_markup": post.reply_markup,
        }
        if post.media_type in [MediaType.VIDEO_NOTE, MediaType.STICKER]:
            params.pop("caption")
        return await method(**params)


async def spamming(bot: Bot, scheduler: AsyncIOScheduler, chat_id: int, post_id: int):
    async with get_session() as session:
        async with session.begin():
            post = await session.scalar(select(Post).where(Post.id == post_id))
            if post.status == Status.WORKING and (post.limit == 0 or post.sent < post.limit):
                if post.last_message_id:
                    await delete_message(bot, chat_id, post.last_message_id)
                message = await send_post(bot, post, chat_id)
                post.last_message_id = message.message_id
                post.sent += 1
            else:
                job = scheduler.get_job(f"spam:{chat_id}")
                if job:
                    job.remove()
                post.status = Status.STOPPED
