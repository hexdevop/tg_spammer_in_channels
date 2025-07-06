from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
)
from loguru import logger
from aiogram.exceptions import TelegramBadRequest

from variables import variables


async def set_bot_commands(bot: Bot):
    admin_commands = [
        BotCommand(command="start", description="Панель администратора ⚙️"),
    ]
    for admin_id in variables.admins:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except TelegramBadRequest:
            logger.warning(
                f"Administrator {admin_id} don`t start conversation with bot"
            )
