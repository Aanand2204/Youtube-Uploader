import os
from collections import deque
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["System Diagnostics"])

_LOG_FILE = os.path.join("logs", "app.log")

@router.get("/health", summary="Health check")
async def health_check() -> dict:
    """Returns a simple health status."""
    return {"status": "ok", "service": "youtube-auto-uploader"}

@router.get("/logs", summary="Get recent log lines")
async def get_logs(
    lines: int = Query(default=100, ge=1, le=2000, description="Number of tail lines to return"),
) -> dict:
    """Return the last N lines from app.log for the UI log viewer."""
    if not os.path.isfile(_LOG_FILE):
        return {"lines": [], "total": 0}

    try:
        with open(_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            tail = list(deque(f, maxlen=lines))
        return {"lines": [l.rstrip("\n") for l in tail], "total": len(tail)}
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not read log file: {exc}")

@router.get("/logs/download", summary="Download the full log file")
async def download_logs() -> FileResponse:
    """Download the complete app.log file."""
    if not os.path.isfile(_LOG_FILE):
        raise HTTPException(status_code=404, detail="Log file not found yet.")
    return FileResponse(_LOG_FILE, filename="app.log", media_type="text/plain")
