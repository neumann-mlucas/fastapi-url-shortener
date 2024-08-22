import os

from pydantic_settings import BaseSettings


def get_db_url() -> str:
    return os.getenv("DATABASE_URI", "sqlite+aiosqlite:///database.db")


class Settings(BaseSettings):
    "app global configuration"

    rd_uri: str | None = os.getenv("CACHE_URI")
    db_uri: str | None = os.getenv("DATABASE_URI")


settings = Settings()
