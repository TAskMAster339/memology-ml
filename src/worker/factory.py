"""
Factory for creating services in the worker.
Follows the Factory pattern and DI principles.
"""

from src.config.logging_config import get_logger
from src.config.settings import ConfigManager
from src.core.image_generator import StableDiffusionGenerator
from src.core.llm_client import OllamaClient
from src.services.caption_service import CaptionService
from src.services.meme_service import MemeService
from src.services.name_service import NameService
from src.services.prompt_service import PromptService
from src.utils.image_utils import ImageUtils

logger = get_logger(__name__)


class ServiceFactory:
    """
    Factory for creating services.
    Encapsulates the logic for creating and configuring all services.
    """

    _config: ConfigManager | None = None
    _meme_service: MemeService | None = None

    @classmethod
    def get_config(cls) -> ConfigManager:
        """
        Get singleton instance of ConfigManager.

        Returns:
            Application configuration
        """
        if cls._config is None:
            cls._config = ConfigManager()
            logger.info("ConfigManager initialized in worker")
        return cls._config

    @classmethod
    def create_meme_service(cls) -> MemeService:
        """
        Create MemeService with all dependencies.

        Returns:
            Fully configured MemeService
        """
        if cls._meme_service is not None:
            return cls._meme_service

        try:
            # Get configuration (this is AppConfig)
            config_manager = cls.get_config()
            config = config_manager.config  # <-- IMPORTANT: use .config property

            logger.info(
                "Creating LLM client (Ollama)",
                extra={
                    "model": config.ollama.model,
                    "base_url": config.ollama.base_url,
                    "timeout": config.ollama.timeout,
                },
            )

            # Create LLM client
            llm_client = OllamaClient(
                model=config.ollama.model,
                default_timeout=config.ollama.timeout,
            )

            logger.info(
                "Creating image generator (Stable Diffusion)",
                extra={
                    "base_url": config.stable_diffusion.base_url,
                    "steps": config.stable_diffusion.steps,
                    "width": config.stable_diffusion.width,
                    "height": config.stable_diffusion.height,
                },
            )

            # Create image generator
            image_generator = StableDiffusionGenerator(
                config=config.stable_diffusion,
            )

            logger.info("Creating services (PromptService, CaptionService)...")

            # Create services
            prompt_service = PromptService(llm_client=llm_client)
            caption_service = CaptionService(llm_client=llm_client)
            name_service = NameService(llm_client=llm_client)

            # Create utilities for working with images
            image_utils = ImageUtils()

            logger.info("Creating MemeService - output_dir=%s", config.output_dir)

            # Create main service
            cls._meme_service = MemeService(
                prompt_service=prompt_service,
                caption_service=caption_service,
                name_service=name_service,
                image_generator=image_generator,
                image_utils=image_utils,
                output_dir=config.output_dir,
            )

            logger.info("✅ MemeService created successfully in worker")

        except Exception:
            logger.exception("Error creating MemeService")
            raise
        else:
            return cls._meme_service

    @classmethod
    def reset(cls):
        """
        Reset the factory (for tests or config reload).
        """
        cls._config = None
        cls._meme_service = None
        logger.info("ServiceFactory reset")
