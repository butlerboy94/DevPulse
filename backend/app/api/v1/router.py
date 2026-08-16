# Top-level API router — combines every /api/v1/* endpoint group into one
# router that app/main.py mounts under the /api/v1 prefix.
from fastapi import APIRouter

from app.api.v1.endpoints.analyze import router as analyze_router
from app.api.v1.endpoints.auth import router as auth_router

router = APIRouter()


# GET /api/v1/health — used by Docker Compose's healthcheck and for a quick
# "is the API up" check.
@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "devpulse-api", "version": "0.1.0"}


router.include_router(auth_router)
router.include_router(analyze_router)
