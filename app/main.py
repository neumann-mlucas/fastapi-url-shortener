from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.router import api_router


def create_app() -> FastAPI:
    # initialize app
    app = FastAPI(title="FastApiUrlShortener")

    @app.on_event("startup")
    async def startup():  # initialize database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # add routes
    app.include_router(api_router)

    return app


app = create_app()
