from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app.controller import url_controller

router = APIRouter(prefix="", tags=["Landing Page"])

router.mount(
    "/static", StaticFiles(directory="app/templates", html=True), name="templates"
)


@router.get("/")
async def landing_page():
    "front end, form where the user can register a new URL"
    return FileResponse("app/templates/index.html")


@router.get("/{hash}")
async def redirect(hash: str, db: AsyncSession = Depends(url_controller.get_db)):
    "redirect short link to the orginal URL"
    response = await url_controller.get(hash, db)
    redirect_url = str(response.data.url)
    return RedirectResponse(redirect_url, status_code=302)
