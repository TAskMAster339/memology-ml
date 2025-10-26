"""
Logging system setup module.
Centralized logging for all application modules.
"""

import logging
import sys
from pathlib import Path
from typing import ClassVar


class LoggerManager:
    """
    Logging manager with support for file and console output.
    """

    _loggers: ClassVar[dict] = {}

    @staticmethod
    def setup_logger(
        name: str,
        log_file: str | None = None,
        level: int = logging.INFO,
        file_level: int = logging.INFO,
        console_level: int = logging.INFO,
    ) -> logging.Logger:
        """
        Configures and returns a logger with the specified name.
        Args:
            name: Logger name (usually the module's __name__)
            log_file: Path to the log file (optional)
            level: General logging level
            file_level: Level for file output
            console_level: Level for console output
        Returns:
            Configured logger
        """
        if name in LoggerManager._loggers:
            return LoggerManager._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        # Formatter for logs
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if path is specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        LoggerManager._loggers[name] = logger
        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get an existing logger or create a new one with default settings.
        Args:
            name: Logger name
        Returns:
            Logger
        """
        if name not in LoggerManager._loggers:
            return LoggerManager.setup_logger(name)
        return LoggerManager._loggers[name]
