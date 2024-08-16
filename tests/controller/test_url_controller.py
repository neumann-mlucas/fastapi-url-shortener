import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.controller.url_controller import get_db
from app.main import app
from app.models import Base, UrlModel
from app.repository.url_repository import url_repository


def create_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def populate_db(db):
    url_repository.add("https://foo.com/", db)
    url_repository.add("https://bar.com/", db)


def override_get_db():
    db = create_db()
    populate_db(db)
    try:
        # db.begin()  # start transctions
        yield db
        # db.rollback()  # after each test
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


class TestUrlController:

    def test_get_url(self, client: TestClient):
        response = client.get("/api/v1/AAAAAAAB")
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://foo.com/"

    def test_get_url_not_found(self, client: TestClient):
        response = client.get("/api/v1/ZZZZZZZZ")
        assert response.status_code == 404

    def test_get_all_urls(self, client: TestClient):
        response = client.get("/api/v1/")
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 2

    def test_create_url(self, client: TestClient):
        url_data = {"url": "https://example.com/"}
        response = client.post("/api/v1/", json=url_data)
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://example.com/"

    def test_create_url_already_exists(self, client: TestClient):
        url_data = {"url": "https:/foo.com/"}
        response = client.post("/api/v1/", json=url_data)
        assert response.status_code == 200
        assert response.json()["status"] == "warning"
        assert response.json()["errors"] == "url already in db"

    def test_delete_url(self, client: TestClient):
        response = client.delete("/api/v1/AAAAAAAB")
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://foo.com/"

    def test_delete_url_not_found(self, client: TestClient):
        response = client.delete("/api/v1/ZZZZZZZZ")
        assert response.status_code == 404
        assert response.json()["detail"] == "no register found in db"

    def test_deactivate_url(self, client: TestClient):
        response = client.put(f"/api/v1/deactivate/AAAAAAAB")
        assert response.status_code == 200
        assert response.json()["data"]["on"] is False

    def test_activate_url(self, client: TestClient):
        client.put(f"/api/v1/deactivate/AAAAAAAB")
        response = client.put(f"/api/v1/activate/AAAAAAAB")
        assert response.status_code == 200
        assert response.json()["data"]["on"] is True

    def test_update_url(self, client: TestClient):
        url_data = {"url": "https://example.com/"}
        response = client.put(f"/api/v1/AAAAAAAB", json=url_data)
        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://example.com/"
