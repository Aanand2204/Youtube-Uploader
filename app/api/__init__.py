from fastapi import APIRouter
from app.api.video import router as video_router
from app.api.system import router as system_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(video_router)
api_router.include_router(system_router)
