import tzlocal
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from fluent.runtime import FluentLocalization
from redis.asyncio import Redis

from bot.utils import fluent_loader
from config import config, Config

bot = Bot(
    token=config.bot.token,
    session=AiohttpSession(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML, protect_content=False, link_preview_is_disabled=True
    ),
)

storage = RedisStorage(Redis(host=config.redis.host, db=config.redis.states))

scheduler = ContextSchedulerDecorator(
    AsyncIOScheduler(
        timezone=tzlocal.get_localzone(),
        jobstores={
            "default": RedisJobStore(
                jobs_key="apscheduler.jobs",
                run_times_key="apscheduler.run_times",
                host=config.redis.host,
                db=config.redis.jobs,
            )
        },
    )
)
languages = fluent_loader.get_fluent_localization()


scheduler.ctx.add_instance(bot, Bot)
scheduler.ctx.add_instance(scheduler, AsyncIOScheduler)
scheduler.ctx.add_instance(languages["ru"], FluentLocalization)
scheduler.ctx.add_instance(config, Config)

dp = Dispatcher(
    storage=storage,
    scheduler=scheduler,
    l10n=languages['ru'],
    config=config,
)
