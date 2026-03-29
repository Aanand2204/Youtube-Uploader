"""
File utility helpers.

Provides safe file saving (from UploadFile), unique path generation,
and cleanup functions used across the pipeline.
"""

import os
import uuid
import shutil
from typing import Optional

from fastapi import UploadFile

from app.core.logger import get_logger

logger = get_logger(__name__)

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}


def get_unique_path(directory: str, suffix: str) -> str:
    """
    Generate a unique file path inside `directory` using a UUID filename.

    Args:
        directory: Target directory (must exist or be created beforehand).
        suffix: File extension including the dot, e.g. '.mp4' or '.wav'.

    Returns:
        Absolute path string, e.g. ``uploads/a3f...b9.mp4``.
    """
    os.makedirs(directory, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    return os.path.join(directory, filename)


async def save_upload(file: UploadFile, dest_dir: str) -> str:
    """
    Persist an uploaded file to `dest_dir` with a UUID-based filename.

    Args:
        file: FastAPI ``UploadFile`` instance from the request.
        dest_dir: Target directory path.

    Returns:
        Absolute path to the saved file.

    Raises:
        ValueError: If the file extension is not in ``ALLOWED_VIDEO_EXTENSIONS``.
        IOError: If the file cannot be written to disk.
    """
    original_ext = os.path.splitext(file.filename or "")[1].lower()
    if original_ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{original_ext}'. "
            f"Allowed types: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}"
        )

    dest_path = get_unique_path(dest_dir, original_ext)
    logger.info("Saving uploaded file '%s' → '%s'", file.filename, dest_path)

    try:
        with open(dest_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
    finally:
        await file.close()

    logger.debug("Saved %d bytes to '%s'", os.path.getsize(dest_path), dest_path)
    return dest_path


def cleanup_file(path: Optional[str]) -> None:
    """
    Safely delete a file at `path`, logging a warning if removal fails.

    Args:
        path: Absolute path to the file, or ``None`` (no-op).
    """
    if not path:
        return
    try:
        if os.path.isfile(path):
            os.remove(path)
            logger.debug("Cleaned up temporary file: '%s'", path)
    except OSError as exc:
        logger.warning("Could not remove file '%s': %s", path, exc)
