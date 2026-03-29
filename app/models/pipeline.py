from __future__ import annotations
from dataclasses import dataclass, field
from pydantic import BaseModel

@dataclass
class PipelineResult:
    """Internal result returned between pipeline phases."""
    youtube_url: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    transcript_preview: str = ""
    duration_seconds: float = 0.0
    video_path: str = ""


class PipelineResponse(BaseModel):
    status: str
    youtube_url: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = []
    transcript_preview: str = ""
    duration_seconds: float = 0.0
    video_id: str = ""  # The filename of the uploaded video on server


class PublishRequest(BaseModel):
    video_id: str
    title: str
    description: str
    tags: list[str]


class ErrorResponse(BaseModel):
    status: str = "error"
    step: str
    detail: str
