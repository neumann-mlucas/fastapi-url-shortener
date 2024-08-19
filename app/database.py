from unittest.mock import AsyncMock, MagicMock

from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = {} if settings.env == "PROD" else {"check_same_thread": False}
engine = create_async_engine(settings.db_url, echo=True, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session


async def get_redis():
    if settings.env == "PROD":
        return await aioredis.from_url(settings.cache_url)
    return await gen_dev_cache()


async def gen_dev_cache():
    "dummy developemnet / testing cache. better to use lru from boltons in the future"
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=None)
    cache.delete = AsyncMock(return_value=None)
    return cache
