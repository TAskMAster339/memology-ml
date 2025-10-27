"""
Factory for creating services in the worker.
Follows the Factory pattern and DI principles.
"""

from src.config.logging_config import get_logger
from src.config.settings import ConfigManager
from src.core.image_generator import ImageGenerator
from src.core.llm_client import LLMClient
from src.services.caption_service import CaptionService
from src.services.meme_service import MemeService
from src.services.prompt_service import PromptService

logger = get_logger(__name__)


class ServiceFactory:
    """
    Factory for creating services.
    Encapsulates the logic for creating and configuring all services.
    """

    _config: ConfigManager = None
    _meme_service: MemeService = None

    @classmethod
    def get_config(cls) -> ConfigManager:
        """
        Get the singleton instance of ConfigManager.

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

        config = cls.get_config()

        # Create clients
        llm_client = LLMClient(
            model=config.ollama_model,
            base_url=config.ollama_base_url,
            timeout=config.ollama_timeout,
        )

        image_generator = ImageGenerator(
            base_url=config.sd_base_url,
            steps=config.sd_steps,
            width=config.sd_width,
            height=config.sd_height,
            sampler=config.sd_sampler,
            cfg_scale=config.sd_cfg_scale,
            restore_faces=config.sd_restore_faces,
        )

        # Create services
        prompt_service = PromptService(llm_client=llm_client)
        caption_service = CaptionService(llm_client=llm_client)

        # Create the main service
        cls._meme_service = MemeService(
            prompt_service=prompt_service,
            caption_service=caption_service,
            image_generator=image_generator,
            output_dir=config.output_dir,
        )

        logger.info("MemeService created successfully in worker")
        return cls._meme_service

    @classmethod
    def reset(cls):
        """
        Reset the factory (for tests or configuration reload).
        """
        cls._config = None
        cls._meme_service = None
        logger.info("ServiceFactory reset")
