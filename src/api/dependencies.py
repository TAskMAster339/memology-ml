"""
Dependency Injection for FastAPI.
Follows OOP and IoC (Inversion of Control) principles.
"""

import logging
import uuid
from typing import Annotated

from fastapi import Depends, Header

from src.config.logging_config import get_logger
from src.config.settings import ConfigManager

logger = get_logger(__name__)


class DependencyProvider:
    """Dependency provider for FastAPI."""

    _config: ConfigManager | None = None

    @classmethod
    def get_config(cls) -> ConfigManager:
        """
        Get singleton instance of ConfigManager.

        Returns:
            ConfigManager instance with application settings
        """
        if cls._config is None:
            cls._config = ConfigManager()
            logger.info("ConfigManager initialized")
        return cls._config

    @classmethod
    def get_logger_for_request(cls, request_id: str) -> logging.Logger:
        """
        Get a logger with request context.

        Args:
            request_id: Unique request ID for tracing

        Returns:
            Logger with additional context
        """
        return logging.LoggerAdapter(
            get_logger(__name__),
            {"request_id": request_id},
        )


# Convenient aliases for use in routers
ConfigDep = Annotated[ConfigManager, Depends(DependencyProvider.get_config)]


async def verify_api_key(
    x_api_key: str = Header(None, description="API key for authentication"),
) -> str:
    """
    API key validation (optional).
    Can be used to protect endpoints.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        Valid API key

    Raises:
        HTTPException: If the key is invalid
    """
    # For production: implement real key validation
    # Currently - stub
    if x_api_key is None:
        return None

    return x_api_key


APIKeyDep = Annotated[str, Depends(verify_api_key)]


async def get_request_id(
    x_request_id: str = Header(
        None,
        description="Unique request ID for tracing",
    ),
) -> str:
    """
    Get or generate a unique request ID.

    Args:
        x_request_id: Request ID from header

    Returns:
        Unique request ID
    """
    if x_request_id:
        return x_request_id

    # Generate new ID if not provided
    return str(uuid.uuid4())


RequestIDDep = Annotated[str, Depends(get_request_id)]
