from fastapi import APIRouter

from .controller.system_controller import router as system_router

api_router = APIRouter()

api_router.include_router(system_router)
