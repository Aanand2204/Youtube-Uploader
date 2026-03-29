from __future__ import annotations

import os
import pickle
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────────────────────────────────────

def _authenticate():
    """
    Acquire or refresh YouTube OAuth2 credentials.

    Attempts to load a cached token from ``settings.YOUTUBE_TOKEN_FILE``.
    If the token is missing or expired, initiates the interactive browser
    consent flow and saves the fresh token for future use.

    Returns:
        A ``google.oauth2.credentials.Credentials`` object.

    Raises:
        FileNotFoundError: If ``client_secrets.json`` is not present.
    """
    if not os.path.isfile(settings.CLIENT_SECRETS_PATH):
        raise FileNotFoundError(
            f"YouTube OAuth client secrets not found at '{settings.CLIENT_SECRETS_PATH}'. "
            "Download it from Google Cloud Console → APIs & Services → Credentials."
        )

    credentials = None

    # Try to load cached token
    if os.path.isfile(settings.YOUTUBE_TOKEN_FILE):
        logger.debug("Loading cached YouTube token from '%s'.", settings.YOUTUBE_TOKEN_FILE)
        with open(settings.YOUTUBE_TOKEN_FILE, "rb") as token_file:
            credentials = pickle.load(token_file)

    # Refresh or re-authenticate if necessary
    if credentials and credentials.expired and credentials.refresh_token:
        logger.info("Refreshing expired YouTube OAuth token …")
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        logger.info("Starting YouTube OAuth browser consent flow …")
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.CLIENT_SECRETS_PATH,
            scopes=settings.YOUTUBE_SCOPES,
        )
        credentials = flow.run_local_server(port=0)

    # Persist the (new/refreshed) token
    os.makedirs(os.path.dirname(settings.YOUTUBE_TOKEN_FILE), exist_ok=True)
    with open(settings.YOUTUBE_TOKEN_FILE, "wb") as token_file:
        pickle.dump(credentials, token_file)
    logger.debug("YouTube token saved to '%s'.", settings.YOUTUBE_TOKEN_FILE)

    return credentials


# ──────────────────────────────────────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────────────────────────────────────

def _build_resource_body(
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",  # 22 = People & Blogs
    privacy_status: str = "private",  # safe default — change to "public" when ready
) -> dict:
    return {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }


async def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    privacy_status: str = "private",
    category_id: str = "22",
) -> str:
    """
    Upload a video to YouTube and return its public URL.

    The upload uses resumable chunked transfer so large files are handled
    safely.  Authentication is handled automatically (see module docstring).

    Args:
        video_path: Absolute path to the video file to upload.
        title: YouTube video title (max 100 chars).
        description: YouTube video description.
        tags: List of tag strings.
        privacy_status: ``"private"``, ``"unlisted"``, or ``"public"``.
        category_id: YouTube category ID (default ``"22"`` = People & Blogs).

    Returns:
        The canonical YouTube watch URL: ``https://www.youtube.com/watch?v=<id>``

    Raises:
        FileNotFoundError: If ``video_path`` does not exist.
        RuntimeError: If the upload fails or the API returns an error.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found for upload: '{video_path}'")

    logger.info("Authenticating with YouTube …")
    credentials = _authenticate()

    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)

    body = _build_resource_body(title, description, tags, category_id, privacy_status)
    media = MediaFileUpload(
        video_path,
        chunksize=4 * 1024 * 1024,  # 4 MB chunks
        resumable=True,
        mimetype="video/*",
    )

    logger.info(
        "Starting YouTube upload | title='%s' | privacy='%s'", title, privacy_status
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.debug("Upload progress: %.1f%%", status.progress() * 100)
    except Exception as exc:
        logger.exception("YouTube upload failed: %s", exc)
        raise RuntimeError(f"YouTube upload error: {exc}") from exc

    video_id: Optional[str] = response.get("id")
    if not video_id:
        raise RuntimeError("YouTube API did not return a video ID.")

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info("Upload successful! Video ID: '%s' | URL: %s", video_id, youtube_url)
    return youtube_url
