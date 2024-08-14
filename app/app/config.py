from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    "temporary dev configuration"
    db_url = "sqlite:///database.db"


settings = Settings()
