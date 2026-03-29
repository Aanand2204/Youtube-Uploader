"""
Entry point for the YouTube Auto-Uploader service.

Run with:
    python main.py

Or directly via uvicorn:
    uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import asyncio
import uvicorn

# ── Inject FFMPEG_PATH bin directory into PATH early ──────────────────────────
# Whisper calls ffmpeg internally as a subprocess. If ffmpeg is not on PATH
# (common with WinGet installs), we must add its directory to os.environ["PATH"]
# here so ALL child processes inherit it — including Whisper's audio loader.
from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_ffmpeg_exe = os.environ.get("FFMPEG_PATH", "")
if _ffmpeg_exe and os.path.isfile(_ffmpeg_exe):
    _ffmpeg_bin = os.path.dirname(_ffmpeg_exe)
    if _ffmpeg_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")

# ── Windows asyncio fix ────────────────────────────────────────────────────────
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

