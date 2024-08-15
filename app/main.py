from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.router import api_router


def create_app() -> FastAPI:
    # initialize app
    app = FastAPI(title="FastApiUrlShortener")

    # create sql tables
    Base.metadata.create_all(bind=engine)

    # add routes
    app.include_router(api_router)

    return app


app = create_app()
