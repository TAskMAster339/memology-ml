"""
Module for configuring and initializing logging.
Supports configuration from logging.ini file and programmatic setup.
"""

import logging
import logging.config
import logging.handlers
from pathlib import Path


class LoggingConfigurator:
    """Class for centralized logging configuration."""

    _configured = False

    @classmethod
    def configure(
        cls,
        config_file: str | None = "logging.ini",
        log_level: str | None = None,
    ) -> None:
        """
        Configures logging for the entire application.

        Args:
            config_file: Path to the configuration file (default is logging.ini)
            log_level: Logging level (overrides configuration from file)
        """
        if cls._configured:
            return

        # Create logs directory if it does not exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # If a config file is specified and exists
        if config_file and Path(config_file).exists():
            try:
                logging.config.fileConfig(config_file, disable_existing_loggers=False)
                cls._configured = True
                logger = logging.getLogger(__name__)
                logger.info("Logging configured from %s", config_file)
            except Exception:
                # Fallback to basic configuration
                cls._configure_basic(log_level)
                logger = logging.getLogger(__name__)
                logger.exception("Failed to load logging config from %s", config_file)
        else:
            cls._configure_basic(log_level)

        # Override level if specified
        if log_level:
            logging.getLogger().setLevel(getattr(logging, log_level.upper()))

    @classmethod
    def _configure_basic(cls, log_level: str | None = None) -> None:
        """Basic logging configuration without a file."""
        level = getattr(logging, log_level.upper()) if log_level else logging.INFO

        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.handlers.RotatingFileHandler(
                    "logs/app.log",
                    maxBytes=10485760,  # 10MB
                    backupCount=5,
                    encoding="utf-8",
                ),
            ],
        )
        cls._configured = True
        logger = logging.getLogger(__name__)
        logger.info("Logging configured with basic settings")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.

        Args:
            name: Logger name (usually __name__ of the module)

        Returns:
            Configured logger instance
        """
        if not cls._configured:
            cls.configure()

        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger.

    Args:
        name: Logger name (recommended to use __name__)

    Returns:
        Logger instance

    Example:
        >>> from src.config.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return LoggingConfigurator.get_logger(name)
