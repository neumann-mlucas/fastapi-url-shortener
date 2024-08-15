from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
def health():
    return True
