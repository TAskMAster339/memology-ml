"""
Entry point for the meme generation application.
"""

import logging
import sys
from pathlib import Path

from src.services.name_service import NameService

# Add src to import path
sys.path.insert(0, str(Path(__file__).parent))
from src.config.settings import ConfigManager
from src.core.image_generator import StableDiffusionGenerator
from src.core.llm_client import OllamaClient
from src.services.caption_service import CaptionService
from src.services.meme_service import MemeService
from src.services.prompt_service import PromptService
from src.utils.image_utils import ImageUtils
from src.utils.logger import LoggerManager


def create_meme_service() -> MemeService:
    """
    Factory function for creating the meme service with all dependencies.
    Returns:
    Fully configured MemeService
    """
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Set up logging
    LoggerManager.setup_logger(
        "memology-ml",
        log_file=config.log_file,
        level=logging.INFO,
    )

    # Create LLM client
    llm_client = OllamaClient(
        model=config.ollama.model,
        default_timeout=config.ollama.timeout,
    )

    # Create image generator
    image_generator = StableDiffusionGenerator(config.stable_diffusion)

    # Create services
    prompt_service = PromptService(llm_client)
    caption_service = CaptionService(llm_client)
    name_service = NameService(llm_client)

    # Create utilities
    image_utils = ImageUtils(font_path=config.font_path)

    # Create main service
    return MemeService(
        prompt_service=prompt_service,
        caption_service=caption_service,
        name_service=name_service,
        image_generator=image_generator,
        image_utils=image_utils,
        output_dir=config.output_dir,
    )


def main():
    """Main function of the application."""
    logger = LoggerManager.get_logger(__name__)

    # Create service
    meme_service = create_meme_service()

    # Examples for generation
    examples = [
        "кот пьет кофе",
        "лошадь чихнула",
        "компьютер и ежу понятен",
    ]

    # Generate memes
    for example in examples:
        logger.info(f"\n{'=' * 60}")  # noqa: G004
        logger.info(f"Generating meme for: {example}")  # noqa: G004
        logger.info(f"{'=' * 60}\n")  # noqa: G004
        result = meme_service.generate_meme(example)
        if result.success:
            print("\n✅ Meme created successfully!")
            print(f"📝 Caption: {result.caption}")
            print(f"🖼️File: {result.final_image_path}")
            print(f"⏱️Time: {result.generation_time:.2f}s\n")
        else:
            print(f"\n❌ Error creating meme: {result.error_message}\n")


if __name__ == "__main__":
    main()
