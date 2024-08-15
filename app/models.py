from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, Integer, String

from app.database import Base


class UrlRegister(Base):
    __tablename__ = "urls"
    idx = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False, unique=True)


class UrlModel(BaseModel):
    "table id should not be visiable to the services"
    hash: str = Field(min_length=8, max_length=8)
    url: HttpUrl