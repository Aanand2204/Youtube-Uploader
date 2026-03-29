from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    """Structured YouTube metadata produced by the LLM."""

    title: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Engaging YouTube video title (max 100 chars).",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Detailed YouTube video description.",
    )
    tags: list[str] = Field(
        ...,
        min_length=3,
        max_length=500,
        description="List of relevant YouTube tags (3 – 15 items).",
    )
