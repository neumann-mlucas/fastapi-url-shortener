import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.controller.url_controller import get_db
from app.main import app
from app.models import Base, UrlModel
from app.repository.url_repository import url_repository
from app.utils.hash import to_hash

# Setup database engine and session
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

API_PREFIX = "/api/v1"
HASH = {i: to_hash(i) for i in (1, 2, 3, 100)}


# Helper function to populate the database
async def populate_db(db):
    await url_repository.add("https://foo.com/", db)
    await url_repository.add("https://bar.com/", db)
    await url_repository.add("https://disable.com/", db)
    await url_repository.update(UrlModel(hash="AAAAAAAD", url=None, on=False), db)


# Override database dependency for testing
async def override_get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        await populate_db(session)
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://") as client:
        yield client


@pytest.mark.asyncio
class TestUrlController:

    async def test_get_url(self, client: AsyncClient):
        response = await client.get(f"{API_PREFIX}/{HASH[1]}")
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://foo.com/"

    async def test_get_url_not_found(self, client: AsyncClient):
        response = await client.get(f"{API_PREFIX}/{HASH[100]}")
        assert response.status_code == 404

    async def test_get_inactive_url(self, client: AsyncClient):
        response = await client.get(f"{API_PREFIX}/{HASH[3]}")
        assert response.status_code == 404

    async def test_get_all_urls(self, client: AsyncClient):
        response = await client.get(f"{API_PREFIX}/")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 3

    async def test_create_url(self, client: AsyncClient):
        url_data = {"url": "https://example.com/"}
        response = await client.post(f"{API_PREFIX}/", json=url_data)
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://example.com/"

    async def test_create_url_already_exists(self, client: AsyncClient):
        url_data = {"url": "https:/foo.com/"}
        response = await client.post(f"{API_PREFIX}/", json=url_data)
        assert response.status_code == 200
        assert response.json()["status"] == "warning"
        assert response.json()["errors"] == "URL already in database"

    async def test_delete_url(self, client: AsyncClient):
        response = await client.delete(f"{API_PREFIX}/{HASH[1]}")
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://foo.com/"

    async def test_delete_url_not_found(self, client: AsyncClient):
        response = await client.delete(f"{API_PREFIX}/{HASH[100]}")
        assert response.status_code == 404
        assert response.json()["detail"] == "No record found to delete"

    async def test_deactivate_url(self, client: AsyncClient):
        response = await client.put(f"{API_PREFIX}/deactivate/{HASH[1]}")
        assert response.status_code == 200
        assert response.json()["data"]["on"] is False

    async def test_activate_url(self, client: AsyncClient):
        await client.put(f"{API_PREFIX}/deactivate/{HASH[1]}")
        response = await client.put(f"{API_PREFIX}/activate/{HASH[1]}")
        assert response.status_code == 200
        assert response.json()["data"]["on"] is True

    async def test_update_url(self, client: AsyncClient):
        url_data = {"url": "https://example.com/"}
        response = await client.put(f"{API_PREFIX}/{HASH[1]}", json=url_data)
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://example.com/"
