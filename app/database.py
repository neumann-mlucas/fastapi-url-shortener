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
