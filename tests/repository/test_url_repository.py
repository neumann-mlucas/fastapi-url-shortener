import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.repository.url_repository import url_repository


# Fixture to set up an in-memory SQLite database and provide a session
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestUrlRepository:

    def test_add_url(self, db_session):
        url = "https://example.com/"
        result = url_repository.add(url, db_session)

        assert result is not None
        assert str(result.url) == url

    def test_add_duplicated_url(self, db_session):
        url = "https://example.com/"
        result = url_repository.add(url, db_session)

        assert result is not None
        assert str(result.url) == url

        url = "https://example.com/"
        result = url_repository.add(url, db_session)

        assert result is None

    def test_get_url_by_hash(self, db_session):
        url = "https://example.com/"
        result = url_repository.add(url, db_session)

        retrieved = url_repository.get(result.hash, db_session)

        assert retrieved is not None
        assert str(retrieved.url) == url

    def test_missing_get_url_by_hash(self, db_session):
        retrieved = url_repository.get("AAAAAAAA", db_session)
        assert retrieved is None

    def test_get_url_by_url(self, db_session):
        url = "https://example.com/"
        url_repository.add(url, db_session)

        retrieved = url_repository.get_by_url(url, db_session)

        assert retrieved is not None
        assert str(retrieved.url) == url

    def test_missing_get_url_by_url(self, db_session):
        retrieved = url_repository.get_by_url("https://example.com/", db_session)
        assert retrieved is None

    def test_delete_url(self, db_session):
        url = "https://example.com/"
        result = url_repository.add(url, db_session)

        url_repository.delete(result.hash, db_session)

        retrieved = url_repository.get(result.hash, db_session)
        assert retrieved is None
