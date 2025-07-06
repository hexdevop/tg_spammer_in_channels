from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from config import config

engine = create_async_engine(
    url=config.database.database_url, echo=False, pool_size=20, max_overflow=10
)

db = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncSession:
    async with db() as session:
        yield session


async def dispose_engines():
    await engine.dispose()
