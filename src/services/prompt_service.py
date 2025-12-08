"""
Service for generating image prompts based on user ideas.
"""

import re

from src.config.logging_config import get_logger
from src.core.llm_client import BaseLLMClient
from src.models.meme import MemeStyle


class PromptService:
    """Service for generating visual prompts for images."""

    SYSTEM_PROMPT = """
    You are a professional prompt engineer for Stable Diffusion specialized in creating hilarious and funny meme images.
    Your task is to transform user ideas into visually entertaining, absurd, and comedic prompts.

    Requirements:
    - Output only the prompt text — one paragraph, no formatting, no quotes, no explanations.
    - The style must be humorous, absurd, exaggerated, or ironical.
    - Include details about lighting, mood, color palette, and depth of field.
    - Use rendering styles that enhance comedy:
    "cartoon style", "anime style", "pop art", "digital art", "exaggerated proportions", "slapstick humor"
    - Adapt the humor style to the topic:
    - Use "cartoon exaggerated" or "absurd humor" for ridiculous or surreal ideas;
    - Use "sarcastic realism" or "deadpan" for ironic commentary;
    - Use "anime comedy" or "chibi style" for cute but funny moments.
    - Add comedic elements:
    "awkward pose", "funny expression", "over-the-top emotion", "unexpected detail", "ironic juxtaposition"
    - Mention a suitable camera angle (e.g., "close-up of face", "wide shot showing chaos", "awkward angle", "slow-motion effect")
    - Include dramatic or exaggerated lighting that enhances the humor
    - Never use markdown, colons, explanations, or any meta instructions.
    - The text should be directly usable as a Stable Diffusion prompt and result in a funny, engaging image.
    """  # noqa: E501

    def __init__(self, llm_client: BaseLLMClient):
        """
        Initializes the prompt service.

        Args:
            llm_client: Client for interacting with LLM
        """
        self.llm_client = llm_client
        self.logger = get_logger(__name__)

    def generate_visual_prompt(
        self,
        user_text: str,
        style: MemeStyle,
        max_retries: int = 1,
    ) -> str:
        """
        Generates a visual prompt in English.

        Args:
            user_text: User idea in Russian
            style: Image style
            max_retries: Maximum number of attempts on errors

        Returns:
            Ready prompt for Stable Diffusion
        """
        self.logger.info(f"Generating visual prompt for: {user_text}")  # noqa: G004

        messages = self._build_messages(user_text, style)

        for attempt in range(max_retries + 1):
            try:
                raw_prompt = self.llm_client.generate(messages, timeout=60)
                cleaned = self._clean_prompt(raw_prompt)

                # Check for Cyrillic characters
                if self._contains_cyrillic(cleaned):
                    if attempt < max_retries:
                        self.logger.warning(
                            "Prompt contains Cyrillic, retrying "
                            "with explicit instruction",
                        )
                        messages = self._build_messages(
                            f"{user_text}. Answer ONLY in English.",
                            style,
                        )
                        continue
                    self.logger.warning(
                        "Prompt still contains Cyrillic after retries",
                    )

            except Exception:
                self.logger.exception("Error generating prompt")
                if attempt >= max_retries:
                    # Return fallback prompt
                    return self._get_fallback_prompt(user_text, style)
            else:
                self.logger.info(f"Generated prompt: {cleaned[:50]}...")  # noqa: G004
                return cleaned

        return self._get_fallback_prompt(user_text, style)

    def _build_messages(self, user_text: str, style: MemeStyle) -> list[dict[str, str]]:
        """Creates a list of messages for the LLM."""
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Describe this scene in English: {user_text}. "
                f"Style: {style.description}",
            },
        ]

    def _clean_prompt(self, text: str) -> str:
        """
        Удаляет блоки <think> и </think> из текста, включая содержимое между ними.

        Args:
            text (str): Исходный текст с блоками <think>

        Returns:
            str: Текст без блоков <think>
        """  # noqa: RUF002
        # Регулярное выражение для поиска <think>.*?</think> (нежадный поиск)
        pattern = r"<think>.*?</think>"
        cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
        return cleaned_text.strip()

    def _contains_cyrillic(self, text: str) -> bool:
        """Checks for Cyrillic characters."""
        return any("а" <= c.lower() <= "я" for c in text)  # noqa: RUF001

    def _get_fallback_prompt(self, user_text: str, style: MemeStyle) -> str:
        """Returns a fallback prompt in case of errors."""
        return f"A scene depicting: {user_text}, {style.description}"
