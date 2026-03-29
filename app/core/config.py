from __future__ import annotations
import os
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application-wide settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Whisper ────────────────────────────────────────────────────────────
    WHISPER_MODEL: Literal["tiny", "base", "small", "medium", "large"] = "base"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120

    # ── File storage ───────────────────────────────────────────────────────
    FFMPEG_PATH: str = "ffmpeg"
    UPLOAD_DIR: str = "uploads"
    AUDIO_DIR: str = "audio"
    CREDENTIALS_DIR: str = "credentials"

    # ── YouTube ────────────────────────────────────────────────────────────
    YOUTUBE_TOKEN_FILE: str = "credentials/token.pickle"
    YOUTUBE_SCOPES: list[str] = ["https://www.googleapis.com/auth/youtube.upload"]

    # ── Upload limits ──────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 500

    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def CLIENT_SECRETS_PATH(self) -> str:
        return os.path.join(self.CREDENTIALS_DIR, "client_secrets.json")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings: Settings = get_settings()
