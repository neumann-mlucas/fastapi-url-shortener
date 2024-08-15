from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    "temporary dev configuration"
    db_url: str = "sqlite:///database.db"


settings = Settings()
