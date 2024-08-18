import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, UrlModel
from app.repository.url_repository import url_repository

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# Fixture to set up an in-memory SQLite database and provide a session
@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
class TestUrlRepository:

    async def test_add_url(self, db_session):
        url = "https://example.com/"
        result = await url_repository.add(url, db_session)

        assert result is not None
        assert str(result.url) == url

    async def test_add_duplicated_url(self, db_session):
        url = "https://example.com/"
        result = await url_repository.add(url, db_session)

        assert result is not None
        assert str(result.url) == url

        url = "https://example.com/"
        result = await url_repository.add(url, db_session)

        assert result is None

    async def test_get_url_by_hash(self, db_session):
        url = "https://example.com/"
        result = await url_repository.add(url, db_session)

        retrieved = await url_repository.get(result.hash, db_session)

        assert retrieved is not None
        assert str(retrieved.url) == url

    async def test_missing_get_url_by_hash(self, db_session):
        retrieved = await url_repository.get("AAAAAAAA", db_session)
        assert retrieved is None

    async def test_get_url_by_url(self, db_session):
        url = "https://example.com/"
        await url_repository.add(url, db_session)

        retrieved = await url_repository.get_by_url(url, db_session)

        assert retrieved is not None
        assert str(retrieved.url) == url

    async def test_missing_get_url_by_url(self, db_session):
        retrieved = await url_repository.get_by_url("https://example.com/", db_session)
        assert retrieved is None

    async def test_delete_url(self, db_session):
        url = "https://example.com/"
        result = await url_repository.add(url, db_session)

        await url_repository.delete(result.hash, db_session)

        retrieved = await url_repository.get(result.hash, db_session)
        assert retrieved is None

    async def test_update_url(self, db_session):
        result = await url_repository.add("https://foo.com/", db_session)

        url = "https://bar.com/"
        await url_repository.update(
            UrlModel(hash=result.hash, url=url, on=None), db_session
        )

        retrieved = await url_repository.get(result.hash, db_session)
        assert retrieved is not None
        assert str(retrieved.url) == url

    async def test_update_active_status(self, db_session):
        result = await url_repository.add("https://foo.com/", db_session)
        await url_repository.update(
            UrlModel(hash=result.hash, url=None, on=False), db_session
        )

        retrieved = await url_repository.get(result.hash, db_session)
        assert retrieved is not None
        assert not retrieved.on
