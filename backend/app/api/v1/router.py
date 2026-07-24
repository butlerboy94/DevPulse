from fastapi import APIRouter

from app.api.v1.endpoints.analyze import router as analyze_router
from app.api.v1.endpoints.auth import router as auth_router

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "devpulse-api", "version": "0.1.0"}


router.include_router(auth_router)
router.include_router(analyze_router)
