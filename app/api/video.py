import os
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.logger import get_logger
from app.models.pipeline import PipelineResponse, PublishRequest
from app.services.orchestrator import PipelineError, prepare_metadata, publish_to_youtube, run_pipeline
from app.utils.file_utils import cleanup_file, save_upload

logger = get_logger(__name__)
router = APIRouter(tags=["Video Operations"])

@router.post(
    "/process-video",
    response_model=PipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Phase 1: Process video to generate AI metadata suggestions",
)
async def process_video(
    file: UploadFile = File(..., description="Video file to upload"),
) -> PipelineResponse:
    """Uploads video and runs Phase 1 (extraction, transcription, metadata)."""
    logger.info("🎬 Phase 1 start: %s", file.filename)
    
    video_path = await save_upload(file, settings.UPLOAD_DIR)
    
    try:
        result = await prepare_metadata(video_path)
        return PipelineResponse(
            status="success",
            title=result.title,
            description=result.description,
            tags=result.tags,
            transcript_preview=result.transcript_preview,
            duration_seconds=result.duration_seconds,
            video_id=os.path.basename(video_path),
        )
    except Exception as exc:
        cleanup_file(video_path)
        logger.exception("Phase 1 failed: %s", exc)
        if isinstance(exc, PipelineError):
            raise HTTPException(500, f"Processing failed at '{exc.step}': {exc.cause}")
        raise HTTPException(500, str(exc))


@router.post(
    "/publish-video",
    response_model=PipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Phase 2: Finalize and publish to YouTube",
)
async def publish_video(req: PublishRequest) -> PipelineResponse:
    """Runs Phase 2 (YouTube upload) with user-confirmed metadata."""
    logger.info("📤 Phase 2 start: %s", req.video_id)
    
    video_path = os.path.join(settings.UPLOAD_DIR, req.video_id)
    if not os.path.exists(video_path):
        raise HTTPException(404, "Video file not found. It may have expired.")

    try:
        youtube_url = await publish_to_youtube(
            video_path=video_path,
            title=req.title,
            description=req.description,
            tags=req.tags
        )
        return PipelineResponse(
            status="success",
            youtube_url=youtube_url,
            title=req.title,
            description=req.description,
            tags=req.tags,
            video_id=req.video_id
        )
    except Exception as exc:
        logger.exception("Phase 2 failed: %s", exc)
        if isinstance(exc, PipelineError):
            raise HTTPException(500, f"Publishing failed at '{exc.step}': {exc.cause}")
        raise HTTPException(500, str(exc))
    finally:
        cleanup_file(video_path)


@router.post(
    "/upload-video",
    response_model=PipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="[LEGACY] Upload and Publish in one step",
)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload"),
) -> PipelineResponse:
    """Combined Phase 1 & 2 (original behavior)."""
    video_path = await save_upload(file, settings.UPLOAD_DIR)
    try:
        result = await run_pipeline(video_path)
        return PipelineResponse(
            status="success",
            youtube_url=result.youtube_url,
            title=result.title,
            description=result.description,
            tags=result.tags,
            transcript_preview=result.transcript_preview,
            duration_seconds=result.duration_seconds,
        )
    finally:
        cleanup_file(video_path)
