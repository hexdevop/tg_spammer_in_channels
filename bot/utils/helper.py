import re
import string
import random
from aiogram import types, exceptions, Bot


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

