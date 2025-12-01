"""
Pydantic schemas for API validation and serialization.
Follow OOP and data validation principles.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from src.templates.memes import DEFAULT_HEIGHT, DEFAULT_WIDTH


class TaskStatus(str, Enum):
    """Celery task statuses."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class MemeGenerationRequest(BaseModel):
    """
    Meme generation request.

    Attributes:
        user_input: Meme description in Russian
        style: Optional visualization style (realistic, anime, cyberpunk, etc.)
    """

    user_input: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Meme description in Russian",
        examples=["cat drinks coffee"],
    )
    style: str | None = Field(
        None,
        description="Visualization style (optional, random if not specified)",
        examples=["realistic", "anime", "cyberpunk"],
    )

    @field_validator("user_input")
    @classmethod
    def validate_user_input(cls, v: str) -> str:
        """Validate user input."""
        v = v.strip()
        if not v:
            raise ValueError
        return v

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {"user_input": "кот пьет кофе", "style": "realistic"},
        }


class TaskResponse(BaseModel):
    """
    Response to task creation.

    Attributes:
        task_id: Unique task identifier
        status: Current task status
        message: Informational message
    """

    task_id: str = Field(..., description="Task UUID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Task information")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "queued",
                "message": "Task added to queue",
            },
        }


class TaskProgressInfo(BaseModel):
    """Task progress information."""

    current: int = Field(..., ge=0, description="Current step")
    total: int = Field(..., ge=0, description="Total steps")
    status: str = Field(..., description="Current status description")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {"current": 2, "total": 4, "status": "Generating image..."},
        }


class MemeGenerationResult(BaseModel):
    """Successful meme generation result."""

    success: bool = Field(default=True, description="Success flag")
    final_image_path: str = Field(
        ...,
        description="Path to the generated image",
    )
    caption: str = Field(..., description="Meme caption")
    style: str = Field(..., description="Used style")
    user_input: str = Field(..., description="Original user request")
    generation_id: str = Field(..., description="Unique generation ID")
    generated_at: str | None = Field(None, description="Generation time")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "success": True,
                "final_image_path": "generated_images/abc123.jpg",
                "caption": "Когда проснулся в понедельник",
                "style": "realistic",
                "user_input": "кот пьет кофе",
                "generation_id": "abc123",
                "generated_at": "2025-10-27T14:30:00Z",
            },
        }


class TaskStatusResponse(BaseModel):
    """
    Detailed information about task status.

    Attributes:
        task_id: Task UUID
        status: Status from TaskStatus enum
        progress: Progress information (if task is running)
        result: Generation result (if task is finished)
        error: Error information (if task failed)
    """

    task_id: str
    status: TaskStatus
    progress: TaskProgressInfo | None = None
    result: MemeGenerationResult | None = None
    error: str | None = None

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "SUCCESS",
                "result": {
                    "success": True,
                    "final_image_path": "generated_images/abc123.jpg",
                    "caption": "Когда проснулся в понедельник",
                    "style": "realistic",
                    "user_input": "кот пьет кофе",
                    "generation_id": "abc123",
                },
            },
        }


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "status": "healthy",
                "service": "memology-ml-api",
                "version": "1.0.0",
                "timestamp": "2025-10-27T14:30:00Z",
            },
        }


class ErrorResponse(BaseModel):
    """Standard error format."""

    detail: str = Field(..., description="Error description")
    error_code: str | None = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "detail": "Image file not found",
                "error_code": "IMAGE_NOT_FOUND",
                "timestamp": "2025-10-27T14:30:00Z",
            },
        }


class MemegenRequest(BaseModel):
    """Request schema for memegen.link meme generation"""

    context: str = Field(
        ...,
        description="Context or situation for the meme",
        min_length=1,
        max_length=500,
        examples=["Когда код работает с первого раза", "Понедельник утром"],  # noqa: RUF001
    )
    width: int = Field(
        default=DEFAULT_WIDTH,
        ge=200,
        le=2000,
        description="Meme width in pixels",
    )
    height: int = Field(
        default=DEFAULT_HEIGHT,
        ge=200,
        le=2000,
        description="Meme height in pixels",
    )


class MemegenResponse(BaseModel):
    """Response schema for memegen.link meme generation"""

    url: str = Field(..., description="URL to the generated meme on memegen.link")
    template: str = Field(
        ...,
        description="Template ID that was used (e.g., 'drake', 'stonks')",
    )
    text: str = Field(..., description="Text placed on the the meme")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "url": "https://api.memegen.link/images/drake/Дебажить_3_часа/Код_работает_с_первого_раза.png?font=notosans&width=800&height=600",
                "template": "drake",
                "text": "Дебажить 3 часа",
            },
        }
