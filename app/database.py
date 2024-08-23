from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_async_engine(settings.db_uri, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session


pool = aioredis.ConnectionPool.from_url(settings.rd_uri)


async def get_redis():
    rd = await aioredis.Redis(connection_pool=pool)
    try:
        yield rd
    finally:
        await rd.close()
