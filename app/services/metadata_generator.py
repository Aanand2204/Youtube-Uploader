from __future__ import annotations

import json
import re
from typing import Any

import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.models.metadata import VideoMetadata

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Prompt template
# ──────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an expert YouTube content strategist and SEO specialist.
Your task is to generate compelling YouTube metadata from a video transcript.

RULES:
- Respond ONLY with a single valid JSON object — no markdown fences, no explanations.
- The JSON must have exactly three keys: "title", "description", "tags".
- "title"       : string, max 100 characters, catchy and SEO-optimised.
- "description" : string, 150–500 words, keyword-rich, includes a brief summary,
                  key takeaways, and a call to action.
- "tags"        : JSON array of 5–15 lowercase tag strings, each ≤ 30 chars.

EXAMPLE OUTPUT:
{
  "title": "How to Master Python in 30 Days",
  "description": "In this video, we explore ...",
  "tags": ["python tutorial", "learn python", "programming"]
}
"""

_USER_PROMPT_TEMPLATE = """\
Generate YouTube metadata for the following transcript:

---
{transcript}
---

Respond ONLY with the JSON object as described.
"""


# ──────────────────────────────────────────────────────────────────────────────
# Core function
# ──────────────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict[str, Any]:
    """
    Attempt to extract and optionally repair a JSON object from an LLM response.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", text).strip()

    # Try to find the start of the JSON object
    start_idx = cleaned.find("{")
    if start_idx == -1:
        raise ValueError("No JSON object found in response.")
    
    cleaned = cleaned[start_idx:]
    
    # Simple repair: if it ends with ] but no }, it's likely truncated after the tags array
    if cleaned.count("{") > cleaned.count("}"):
        if cleaned.strip().endswith("]"):
            cleaned += "\n}"
        elif not cleaned.strip().endswith("}"):
            # Try to find the last valid structure and close it
            # This is a fallback for very messy truncation
            last_bracket = max(cleaned.rfind("]"), cleaned.rfind("\""))
            if last_bracket != -1:
                cleaned = cleaned[:last_bracket+1]
                if cleaned.strip().endswith("\""): # Inside a string
                    cleaned += "\n}"
                else: # Likely after an array or value
                    cleaned += "\n}"

    # Try to locate the last } to catch cases with trailing text
    end_idx = cleaned.rfind("}")
    if end_idx != -1:
        cleaned = cleaned[:end_idx + 1]

    return json.loads(cleaned)


async def generate_metadata(transcript: str) -> VideoMetadata:
    """
    Generate a YouTube title, description, and tags from a transcript.
    """
    if not transcript or not transcript.strip():
        logger.warning("Empty transcript received — using placeholder metadata.")
        return VideoMetadata(
            title="Untitled Video",
            description="No transcript was available to generate a description.",
            tags=["video", "content", "upload"],
        )

    prompt = _USER_PROMPT_TEMPLATE.format(transcript=transcript[:6000])

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": f"{_SYSTEM_PROMPT}\n\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 2048,  # Increased to prevent truncation
        },
    }

    logger.info(
        "Requesting metadata from Ollama (model='%s') …", settings.OLLAMA_MODEL
    )

    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
            )
            response.raise_for_status()
    except httpx.ConnectError as exc:
        raise RuntimeError(
            f"Cannot connect to Ollama at '{settings.OLLAMA_BASE_URL}'. "
            "Make sure Ollama is running."
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text}"
        ) from exc
    except httpx.TimeoutException as exc:
        raise RuntimeError(
            f"Ollama request timed out after {settings.OLLAMA_TIMEOUT}s."
        ) from exc

    raw_response = response.json().get("response", "")
    logger.debug("Ollama raw response: %s", raw_response[:500])

    try:
        data = _extract_json(raw_response)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse LLM response as JSON: %s", raw_response)
        raise RuntimeError(f"LLM returned invalid JSON: {exc}") from exc

    try:
        metadata = VideoMetadata(**data)
    except ValidationError as exc:
        logger.error("LLM response failed schema validation: %s", exc)
        raise RuntimeError(f"Metadata validation failed: {exc}") from exc

    logger.info("Metadata generated — title: '%s', tags: %s", metadata.title, metadata.tags)
    return metadata
