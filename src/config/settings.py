"""
The application configuration management module.
Uses environment variables and provides default values.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OllamaConfig:
    """Configuration for Ollama LLM."""

    model: str = "llama3.2:3b"
    timeout: int = 15
    base_url: str = "http://localhost:11434"


@dataclass
class StableDiffusionConfig:
    """Configuration for Stable Diffusion WebUI."""

    base_url: str = "http://127.0.0.1:7860"
    steps: int = 20
    width: int = 512
    height: int = 512
    sampler: str = "DPM++ 2M Karras"
    cfg_scale: float = 7.0
    restore_faces: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""

    output_dir: str = "generated_images"
    log_file: str = "generation.log"
    font_path: str = "impact.ttf"
    ollama: OllamaConfig = None
    stable_diffusion: StableDiffusionConfig = None

    def __post_init__(self):
        if self.ollama is None:
            self.ollama = OllamaConfig()
        if self.stable_diffusion is None:
            self.stable_diffusion = StableDiffusionConfig()
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """
    Configuration manager with environment variable support.
    Singleton pattern for a single access point to configuration.
    """

    _instance: Optional["ConfigManager"] = None
    _config: AppConfig | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self) -> AppConfig:
        """Loads configuration from environment variables."""
        if self._config is None:
            ollama_config = OllamaConfig(
                model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
                timeout=int(os.getenv("OLLAMA_TIMEOUT", "15")),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
            sd_config = StableDiffusionConfig(
                base_url=os.getenv("SD_BASE_URL", "http://127.0.0.1:7860"),
                steps=int(os.getenv("SD_STEPS", "20")),
                width=int(os.getenv("SD_WIDTH", "512")),
                height=int(os.getenv("SD_HEIGHT", "512")),
                sampler=os.getenv("SD_SAMPLER", "DPM++ 2M Karras"),
                cfg_scale=float(os.getenv("SD_CFG_SCALE", "7.0")),
                restore_faces=os.getenv("SD_RESTORE_FACES", "True") == "True",
            )
            self._config = AppConfig(
                output_dir=os.getenv("OUTPUT_DIR", "generated_images"),
                log_file=os.getenv("LOG_FILE", "generation.log"),
                font_path=os.getenv("FONT_PATH", "impact.ttf"),
                ollama=ollama_config,
                stable_diffusion=sd_config,
            )
        return self._config

    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config
