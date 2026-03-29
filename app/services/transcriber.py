from __future__ import annotations

import asyncio
import os
from typing import Any

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Module-level singleton — populated on first call to transcribe()
_whisper_model: Any | None = None
_model_lock = asyncio.Lock()


async def _load_model() -> Any:
    """Load and cache the Whisper model (thread-safe)."""
    global _whisper_model

    async with _model_lock:
        if _whisper_model is None:
            import whisper  # deferred import — heavy dependency

            model_name = settings.WHISPER_MODEL
            logger.info("Loading Whisper model '%s' …", model_name)

            loop = asyncio.get_running_loop()
            _whisper_model = await loop.run_in_executor(
                None, lambda: whisper.load_model(model_name)
            )
            logger.info("Whisper model '%s' loaded successfully.", model_name)

    return _whisper_model


async def transcribe(audio_path: str) -> str:
    """
    Transcribe an audio file to text using Whisper.

    Args:
        audio_path: Absolute path to a ``.wav`` (or other Whisper-supported)
                    audio file.

    Returns:
        The full transcript as a single string.  Returns an empty string if
        Whisper produces no text.

    Raises:
        FileNotFoundError: If ``audio_path`` does not exist.
        RuntimeError: If transcription fails unexpectedly.
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: '{audio_path}'")

    logger.info("Starting transcription for '%s' …", audio_path)
    model = await _load_model()

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: model.transcribe(audio_path, fp16=False),
        )
    except Exception as exc:
        logger.exception("Whisper transcription failed: %s", exc)
        raise RuntimeError(f"Transcription error: {exc}") from exc

    transcript: str = result.get("text", "").strip()
    word_count = len(transcript.split())
    logger.info(
        "Transcription complete — %d words, %d characters.",
        word_count,
        len(transcript),
    )
    logger.debug("Transcript preview: '%s …'", transcript[:200])

    return transcript
