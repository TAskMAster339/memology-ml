"""
Data models for representing memes and related entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class MemeStyle:
    """Image style for a meme."""

    name: str
    description: str

    def __str__(self) -> str:
        return self.description


@dataclass
class MemeGenerationRequest:
    """Request for meme generation."""

    user_input: str
    style: MemeStyle | None = None
    request_id: str = field(default_factory=lambda: uuid4().hex[:8])
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MemeGenerationResult:
    """Meme generation result."""

    request: MemeGenerationRequest
    visual_prompt: str
    caption: str
    name: str
    final_image_path: str
    generation_time: float
    success: bool = True
    error_message: str | None = None

    def to_log_string(self) -> str:
        """Formats the result for logging."""
        return (
            f"Model: {self.request.request_id} | "
            f"Prompt: {self.request.user_input.strip()} | "
            f"Visual: {self.visual_prompt[:100]}... | "
            f"Caption: {self.caption} | "
            f"Name: {self.name} | "
            f"FinalFile: {self.final_image_path} | "
            f"Time: {self.generation_time:.2f}s"
        )


# Predefined styles for generation
PREDEFINED_STYLES = [
    MemeStyle(
        "anime",
        "anime style, vibrant colors, soft lighting, detailed, 4k render",
    ),
    MemeStyle(
        "realistic",
        "ultra realistic, cinematic lighting, shallow depth of field, "
        "photo style, HDR, 8k",
    ),
    MemeStyle(
        "cartoon",
        "cartoon style, exaggerated expressions, colorful, flat shading, "
        "digital illustration",
    ),
    MemeStyle(
        "cyberpunk",
        "cyberpunk, neon lights, futuristic atmosphere, dark streets, "
        "glowing reflections",
    ),
    MemeStyle(
        "fantasy",
        "fantasy art, mystical lighting, ethereal glow, highly detailed, "
        "magical realism",
    ),
    MemeStyle(
        "oil_painting",
        "oil painting, baroque composition, dramatic shadows, rich colors, "
        "textured brushstrokes",
    ),
    MemeStyle("watercolor", "watercolor art, pastel tones, dreamy mood, soft contrast"),
    MemeStyle(
        "pixel_art",
        "pixel art, retro video game vibe, limited palette, crisp edges",
    ),
]
