from __future__ import annotations
import time
from typing import Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.core.exceptions import PipelineError
from app.models.pipeline import PipelineResult
from app.services import video_processor, transcriber, metadata_generator, youtube_uploader
from app.utils.file_utils import cleanup_file

logger = get_logger(__name__)


async def prepare_metadata(video_path: str) -> PipelineResult:
    """
    Phase 1: Process video to generate suggested metadata.
    Does NOT upload to YouTube.
    """
    pipeline_start = time.perf_counter()
    audio_path: Optional[str] = None

    logger.info("═" * 60)
    logger.info("Pipeline Phase 1: Preparation | video='%s'", video_path)
    logger.info("═" * 60)

    try:
        # ── Step 1: Audio extraction ───────────────────────────────────────
        logger.info("▶ Step 1/3 — Audio Extraction")
        step_start = time.perf_counter()
        try:
            audio_path = await video_processor.extract_audio(video_path)
        except Exception as exc:
            raise PipelineError("audio_extraction", exc) from exc
        logger.info("✔ Step 1 done (%.2fs)", time.perf_counter() - step_start)

        # ── Step 2: Transcription ──────────────────────────────────────────
        logger.info("▶ Step 2/3 — Transcription")
        step_start = time.perf_counter()
        try:
            transcript = await transcriber.transcribe(audio_path)
        except Exception as exc:
            raise PipelineError("transcription", exc) from exc
        logger.info("✔ Step 2 done (%.2fs)", time.perf_counter() - step_start)

        # ── Step 3: Metadata generation ────────────────────────────────────
        logger.info("▶ Step 3/3 — Metadata Generation")
        step_start = time.perf_counter()
        try:
            metadata = await metadata_generator.generate_metadata(transcript)
        except Exception as exc:
            raise PipelineError("metadata_generation", exc) from exc
        logger.info("✔ Step 3 done (%.2fs)", time.perf_counter() - step_start)

    finally:
        # Clean up the temporary audio file
        cleanup_file(audio_path)

    total_duration = time.perf_counter() - pipeline_start
    return PipelineResult(
        title=metadata.title,
        description=metadata.description,
        tags=metadata.tags,
        transcript_preview=transcript[:300],
        duration_seconds=round(total_duration, 2),
        video_path=video_path,
    )


async def publish_to_youtube(video_path: str, title: str, description: str, tags: list[str]) -> str:
    """
    Phase 2: Actually upload the video to YouTube with (potentially edited) metadata.
    """
    logger.info("═" * 60)
    logger.info("Pipeline Phase 2: Publishing | video='%s'", video_path)
    logger.info("═" * 60)

    # ── Step 4: YouTube upload ─────────────────────────────────────────
    logger.info("▶ Step 4/4 — YouTube Upload")
    step_start = time.perf_counter()
    try:
        youtube_url = await youtube_uploader.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
        )
    except Exception as exc:
        raise PipelineError("youtube_upload", exc) from exc
    
    logger.info("✔ Step 4 done (%.2fs)", time.perf_counter() - step_start)
    logger.info("═" * 60)
    logger.info("Upload COMPLETE | url=%s", youtube_url)
    logger.info("═" * 60)

    return youtube_url


async def run_pipeline(video_path: str) -> PipelineResult:
    """
    Backward compatibility wrapper for the full single-step pipeline.
    """
    result = await prepare_metadata(video_path)
    url = await publish_to_youtube(
        video_path=video_path,
        title=result.title,
        description=result.description,
        tags=result.tags
    )
    result.youtube_url = url
    return result
