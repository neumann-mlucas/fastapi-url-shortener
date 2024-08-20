import os

from pydantic_settings import BaseSettings


def get_db_url() -> str:
    db_var = "PRD_DATABASE_URI" if os.getenv("ENV") == "PROD" else "DEV_DATABASE_URI"
    return os.getenv(db_var, "sqlite+aiosqlite:///database.db")


class Settings(BaseSettings):
    "app global configuration"

    env: str = os.getenv("ENV", "DEV")
    db_uri: str = get_db_url()
    cache_uri: str = os.getenv("CACHE_URI", "")


settings = Settings()
