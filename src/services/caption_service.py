"""
Service for generating short meme captions.
"""

from src.config.logging_config import get_logger
from src.core.llm_client import BaseLLMClient


class CaptionService:
    """Service for generating meme captions in Russian."""

    SYSTEM_PROMPT = """
    Ты — генератор коротких мемных подписей.
    Создавай короткие смешные подписи на русском языке (2–4 слов).
    Используй сарказм, самоиронию, иронию или жизненные ситуации.
    Не упоминай людей, бренды, политику и не используй грубости.
    Отвечай только подписью, без кавычек и пояснений.
    """  # noqa: RUF001

    def __init__(self, llm_client: BaseLLMClient):
        """
        Initializes the caption service.

        Args:
            llm_client: Client for interacting with LLM
        """
        self.llm_client = llm_client
        self.logger = get_logger(__name__)

    def generate_caption(self, scene_description: str) -> str:
        """
        Generates a short meme caption.

        Args:
            scene_description: Scene description or idea

        Returns:
            Short caption in Russian

        """
        self.logger.info("Generating caption")

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": scene_description},
        ]

        try:
            raw_caption = self.llm_client.generate(messages, timeout=30)
            cleaned = self._clean_caption(raw_caption)

            self.logger.info(f"Generated caption: {cleaned}")  # noqa: G004
        except Exception as e:
            self.logger.exception(f"Error generating caption: {e}")  # noqa: G004, TRY401
            return self._get_fallback_caption()
        else:
            return cleaned

    def _clean_caption(self, text: str) -> str:
        """Cleans the caption and limits its length."""
        cleaned = text.replace("**", "").replace("```", "").strip()
        # Take the first line and limit to 80 characters
        first_line = cleaned.split("\n")[0]
        return first_line[:80]

    def _get_fallback_caption(self) -> str:
        """Returns a fallback caption in case of errors."""
        return "Когда всё пошло не так"
