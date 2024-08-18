from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health():
    return True
