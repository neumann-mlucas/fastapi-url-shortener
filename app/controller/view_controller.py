from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.controller import url_controller

router = APIRouter(prefix="", tags=["Landing Page"])

router.mount(
    "/static", StaticFiles(directory="app/templates", html=True), name="templates"
)


@router.get("/")
async def landing_page():
    return FileResponse("app/templates/index.html")


@router.get("/{hash}")
def redirect(hash: str, db: Session = Depends(url_controller.get_db)):
    response = url_controller.get(hash, db)
    redirect_url = str(response.data.url)
    return RedirectResponse(redirect_url, status_code=302)
