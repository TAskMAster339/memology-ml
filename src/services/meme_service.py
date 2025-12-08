"""
Main service for orchestrating meme generation.
Combines all components for meme creation.
"""

import os
import random
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import requests

from src.config.logging_config import get_logger
from src.core.image_generator import BaseImageGenerator
from src.models.meme import (
    PREDEFINED_STYLES,
    MemeGenerationRequest,
    MemeGenerationResult,
    MemeStyle,
)
from src.services.caption_service import CaptionService
from src.services.name_service import NameService
from src.services.prompt_service import PromptService
from src.utils.image_utils import ImageUtils


class MemeService:
    """
    Main meme generation service.
    Coordinates the work of all components.
    """

    def __init__(
        self,
        prompt_service: PromptService,
        caption_service: CaptionService,
        name_service: NameService,
        image_generator: BaseImageGenerator,
        image_utils: ImageUtils,
        output_dir: str = "generated_images",
    ):
        """
        Initializes the meme service.

        Args:
            prompt_service: Prompt generation service
            caption_service: Caption generation service
            image_generator: Image generator
            image_utils: Image utilities
            output_dir: Directory to save results
        """
        self.prompt_service = prompt_service
        self.caption_service = caption_service
        self.name_service = name_service
        self.image_generator = image_generator
        self.image_utils = image_utils
        self.output_dir = Path(output_dir)
        self.logger = get_logger(__name__)
        # Create directory if it does not exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_meme(
        self,
        user_input: str,
        style: MemeStyle | None = None,
    ) -> MemeGenerationResult:
        """
        Generates a meme based on the user's idea.

        Args:
            user_input: Meme idea from the user
            style: Image style (if None, a random one is chosen)

        Returns:
            Meme generation result
        """
        start_time = time.time()

        # Create request
        request = MemeGenerationRequest(
            user_input=user_input,
            style=style or self._get_random_style(),
        )

        self.logger.info(f"Starting meme generation: {request.request_id}")  # noqa: G004
        self.logger.info(f"User input: {user_input}")  # noqa: G004
        self.logger.info(f"Style: {request.style.name}")  # noqa: G004

        try:
            # 1. Generate visual prompt
            visual_prompt = self.prompt_service.generate_visual_prompt(
                user_input,
                request.style,
            )

            # 2. Generate caption
            caption = self.caption_service.generate_caption(user_input)

            # Generate meme name
            name = self.name_service.generate_name(visual_prompt)

            # 3. Generate image
            raw_image = self.image_generator.generate(visual_prompt)

            # 4. Add caption
            final_image = self.image_utils.add_caption_to_image(raw_image, caption)

            # 5. Save final image
            final_path = self._generate_filename("final")
            self.image_utils.save_image(final_image, final_path)

            # 6. Upload on server
            final_path_on_server = self.upload(
                request.request_id,
                final_path,
                final_image,
            )

            # Calculate generation time
            generation_time = time.time() - start_time

            # Create result
            result = MemeGenerationResult(
                request=request,
                visual_prompt=visual_prompt,
                caption=caption,
                name=name,
                final_image_path=final_path_on_server,
                generation_time=generation_time,
                success=True,
            )
            self.logger.info(result.to_log_string())
            self.logger.info(f"Meme generation completed in {generation_time:.2f}s")  # noqa: G004

        except Exception as e:
            generation_time = time.time() - start_time

            self.logger.error(f"Meme generation failed: {e}", exc_info=True)  # noqa: G004, G201

            return MemeGenerationResult(
                request=request,
                visual_prompt="",
                caption="",
                name="",
                final_image_path="",
                generation_time=generation_time,
                success=False,
                error_message=str(e),
            )
        else:
            return result

    def _get_random_style(self) -> MemeStyle:
        """Returns a random style from the predefined ones."""
        return random.choice(PREDEFINED_STYLES)

    def _generate_filename(self, suffix: str) -> str:
        """
        Generates a unique filename.

        Args:
            suffix: Suffix for the name (e.g., "raw" or "final")

        Returns:
            Full path to the file
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = uuid4().hex[:6]
        filename = f"meme_{timestamp}_{unique_id}_{suffix}.png"

        return str(self.output_dir / filename)

    def upload(self, task_id: str, local_path: str, image) -> str:
        """Loads an image from memory to the server and returns the path on the server."""
        server_api_url = os.getenv("SERVER_API_URL")
        worker_token = os.getenv("WORKER_SECRET_TOKEN")

        if not server_api_url or not worker_token:
            self.logger.warning(
                "SERVER_API_URL or WORKER_SECRET_TOKEN not set. Skipping upload.",
            )
            return local_path

        upload_url = f"{server_api_url}/internal/upload/{task_id}"
        headers = {"X-Worker-Token": worker_token}

        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        try:
            files = {"file": (Path(local_path).name, img_byte_arr, "image/png")}
            response = requests.post(
                upload_url,
                headers=headers,
                files=files,
                timeout=60,
            )
            response.raise_for_status()

            response_data = response.json()
            path_on_server = response_data.get("path_on_server")

            if not path_on_server:
                raise Exception(
                    "Server did not return a valid path for the uploaded file."
                )

            self.logger.info(
                f"Successfully uploaded result for task {task_id}. Path on server: {path_on_server}"
            )
            return path_on_server
        except requests.RequestException as e:
            self.logger.error(f"Failed to upload result for task {task_id}: {e}")
            raise
