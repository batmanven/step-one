from fastapi import APIRouter
from app.api.v1 import process, sessions, upload

router = APIRouter()
router.include_router(process.router, prefix="/process", tags=["Processing"])
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
router.include_router(upload.router, tags=["Upload"])

__all__ = ["router"]
