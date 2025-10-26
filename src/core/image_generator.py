"""
Abstraction for image generation via Stable Diffusion WebUI.
"""

import base64
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

import requests
from PIL import Image

from src.config.settings import StableDiffusionConfig
from src.utils.logger import LoggerManager


class BaseImageGenerator(ABC):
    """Abstract base class for image generators."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> Image.Image:
        """
        Generates an image from a prompt.

        Args:
            prompt: Text description of the image
            **kwargs: Additional generation parameters

        Returns:
            Generated image
        """


class StableDiffusionGenerator(BaseImageGenerator):
    """Image generator via Stable Diffusion WebUI API."""

    def __init__(self, config: StableDiffusionConfig):
        """
        Initializes the generator.

        Args:
            config: Stable Diffusion configuration
        """
        self.config = config
        self.logger = LoggerManager.get_logger(__name__)
        self.api_url = f"{config.base_url}/sdapi/v1/txt2img"

    def generate(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        **kwargs: Any,
    ) -> Image.Image:
        """
        Generates an image via SD WebUI API.

        Args:
            prompt: Description of the desired image
            negative_prompt: Description of unwanted elements
            **kwargs: Additional parameters (override configuration)

        Returns:
            Generated image

        Raises:
            requests.RequestException: On network request errors
        """
        payload = self._build_payload(prompt, negative_prompt, **kwargs)

        try:
            self.logger.info(f"Generating image with prompt: {prompt[:50]}...")  # noqa: G004
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()

            image_base64 = response.json()["images"][0]
            image = Image.open(BytesIO(base64.b64decode(image_base64)))

            self.logger.info("Image generated successfully")
        except requests.RequestException:
            self.logger.exception("Failed to generate image")
            raise
        else:
            return image

    def _build_payload(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Creates a payload for the API request.

        Args:
            prompt: Main prompt
            negative_prompt: Negative prompt
            **kwargs: Override configuration parameters

        Returns:
            Dictionary with generation parameters
        """
        default_negative = (
            "low quality, blurry, bad anatomy, distorted, extra limbs, "
            "poorly drawn, text, watermark, signature, logo"
        )
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt or default_negative,
            "steps": kwargs.get("steps", self.config.steps),
            "width": kwargs.get("width", self.config.width),
            "height": kwargs.get("height", self.config.height),
            "sampler_index": kwargs.get("sampler", self.config.sampler),
            "cfg_scale": kwargs.get("cfg_scale", self.config.cfg_scale),
            "restore_faces": kwargs.get("restore_faces", self.config.restore_faces),
            "batch_size": 1,
            "n_iter": 1,
            "seed": -1,
        }
