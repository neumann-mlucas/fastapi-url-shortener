import os

from pydantic_settings import BaseSettings


def get_db_url() -> str:
    is_prod = os.getenv("ENV") == "PROD"
    db_url = (
        os.getenv("PRD_DATABASE_URL")
        if is_prod
        else os.getenv("DEV_DATABASE_URL", "sqlite:///database.db")
    )
    if db_url is None:
        raise ValueError("no database URL set in enviroment")
    return db_url


class Settings(BaseSettings):
    "temporary dev configuration"
    env: str = os.getenv("ENV", "DEV")
    db_url: str = get_db_url()


settings = Settings()
