import asyncio
import os
import subprocess

from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.logger import get_logger
from app.utils.file_utils import get_unique_path

logger = get_logger(__name__)


def _run_ffmpeg(cmd: list[str]) -> tuple[int, str]:
    """
    Run an FFmpeg command synchronously (called inside a thread executor).

    Returns:
        Tuple of (return_code, stderr_output).
    """
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,  # 10-minute hard cap
        )
        return result.returncode, result.stderr.decode(errors="replace")
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg not found on PATH. "
            "Please install FFmpeg and ensure it is available in your system PATH.\n"
            "Windows: winget install ffmpeg  OR  choco install ffmpeg  "
            "OR  download from https://ffmpeg.org/download.html"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timed out after 10 minutes.")


async def extract_audio(video_path: str) -> str:
    """
    Extract the audio track from a video file using FFmpeg.

    The output is a mono 16 kHz PCM WAV file.  FFmpeg must be installed
    and available on the system ``PATH``.

    Uses ``subprocess.run`` inside a thread-pool executor to remain
    compatible with Windows asyncio event loops.

    Args:
        video_path: Absolute path to the source video file.

    Returns:
        Absolute path to the extracted ``.wav`` audio file.

    Raises:
        FileNotFoundError: If ``video_path`` does not exist.
        RuntimeError: If FFmpeg is not found or exits with a non-zero code.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: '{video_path}'")

    audio_path = get_unique_path(settings.AUDIO_DIR, ".wav")
    logger.info("Extracting audio | video='%s' → audio='%s'", video_path, audio_path)

    cmd = [
        settings.FFMPEG_PATH,  # uses full path from .env if set
        "-y",                   # overwrite output without prompting
        "-i", video_path,
        "-vn",                  # disable video output
        "-acodec", "pcm_s16le", # uncompressed PCM — Whisper-friendly
        "-ar", "16000",         # 16 kHz sample rate
        "-ac", "1",             # mono channel
        audio_path,
    ]

    logger.debug("FFmpeg command: %s", " ".join(cmd))

    loop = asyncio.get_running_loop()
    returncode, stderr_output = await loop.run_in_executor(
        None, _run_ffmpeg, cmd
    )

    if returncode != 0:
        logger.error("FFmpeg failed (code %d):\n%s", returncode, stderr_output.strip())
        raise RuntimeError(
            f"FFmpeg exited with code {returncode}.\n{stderr_output.strip()}"
        )

    size_kb = os.path.getsize(audio_path) / 1024
    logger.info("Audio extracted successfully (%.1f KB): '%s'", size_kb, audio_path)
    return audio_path
