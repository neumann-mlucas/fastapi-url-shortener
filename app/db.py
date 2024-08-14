from sqlmodel import Session, SQLModel, create_engine

from .config import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.db_url, echo=True, connect_args=connect_args)

# initialize database
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
