import asyncio
import sys

from loguru import logger

from bot import handlers, middlewares, dp, bot, scheduler
from bot.utils import helper
from bot.utils.ui_commands import set_bot_commands
from config import config

from variables import variables

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> "
    "<level>{level: <8}</level> <red>|</red> "
    "<level>{message}</level>"
)
logger.remove()  # Удаляем предыдущие конфигурации
logger.add(sys.stdout, format=logger_format)

logger.info(f"Attempting Bot Startup")

handlers.setup(dp)
middlewares.setup(dp)

updates = dp.resolve_used_update_types()
logger.opt(colors=True).info(
    "Allowed updates: <fg #00ccff>[%s]</>" % ", ".join(updates)
)


async def main():
    scheduler.start(paused=False)

    await set_bot_commands(bot)

    variables.username = (await bot.get_me()).username
    logger.info(f"All utils of @{variables.username} STARTED WITH POLLING")

    if config.bot.skip_updates:
        await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=updates)


if __name__ == "__main__":
    asyncio.run(main())
