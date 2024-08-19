from fastapi import APIRouter

from app.controller.system_controller import router as system_router
from app.controller.url_controller import router as url_router
from app.controller.view_controller import router as view_router

api_router = APIRouter()

# health check and monitors
api_router.include_router(system_router)
# internal CRUD operations API
api_router.include_router(url_router)
# user interface
api_router.include_router(view_router)
