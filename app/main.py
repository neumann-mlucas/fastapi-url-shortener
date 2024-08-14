from fastapi import FastAPI

from .router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="FastApiUrlShortener")

    app.include_router(api_router)
    return app


app = create_app()
