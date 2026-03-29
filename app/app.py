from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def _create_directories() -> None:
    """Ensure all required runtime directories exist."""
    dirs = [settings.UPLOAD_DIR, settings.AUDIO_DIR, settings.CREDENTIALS_DIR, "logs"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    logger.debug("Runtime directories verified: %s", dirs)


def create_app() -> FastAPI:
    """Application factory for the YouTube Auto-Uploader."""
    app = FastAPI(
        title="YouTube Auto-Uploader",
        description="AI-powered video-to-YouTube automation pipeline.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # tighten for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes & Statics ──────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Static files (UI) ─────────────────────────────────────────────────
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # ── Root → serve UI ───────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def serve_ui() -> FileResponse:
        return FileResponse(os.path.join(static_dir, "index.html"))

    # ── Lifecycle hooks ───────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        _create_directories()
        logger.info("YouTube Auto-Uploader started successfully.")
        logger.info(
            "Whisper model: '%s' | Ollama model: '%s'",
            settings.WHISPER_MODEL,
            settings.OLLAMA_MODEL,
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("YouTube Auto-Uploader shutting down.")

    return app


app = create_app()
