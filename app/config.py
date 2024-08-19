import os

from pydantic_settings import BaseSettings


def get_db_url() -> str:
    db_var = "PRD_DATABASE_URL" if os.getenv("ENV") == "PROD" else "DEV_DATABASE_URL"
    return os.getenv(db_var, "sqlite+aiosqlite:///database.db")


class Settings(BaseSettings):
    "app global configuration"
    env: str = os.getenv("ENV", "DEV")
    db_url: str = get_db_url()


settings = Settings()
