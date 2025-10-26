"""
Service for generating image prompts based on user ideas.
"""

from src.core.llm_client import BaseLLMClient
from src.models.meme import MemeStyle
from src.utils.logger import LoggerManager


class PromptService:
    """Service for generating visual prompts for images."""

    SYSTEM_PROMPT = """
    You are a professional prompt engineer for Stable Diffusion and your task is to create a
    Requirements:
    - Output only the prompt text — one paragraph, no formatting, no quotes, no explanations.
    - The style must be visually rich and cinematic.
    - Include details about lighting, mood, color palette, and depth of field.
    - Use realistic or artistic rendering styles such as:
    "ultra realistic", "studio lighting", "anime style", "cinematic lighting", "digital art
    - Adapt the style to match the topic:
    - use "anime style" or "cartoon" for fun, lighthearted, or cute topics;
    - use "realistic", "cinematic lighting" for serious, dramatic, or lifelike ideas.
    - Mention a suitable camera angle (e.g., "close-up", "wide shot", "from above", "portrait")
    - Never use markdown, colons, explanations, or any meta instructions.
    - The text should be directly usable as a Stable Diffusion prompt.
    """  # noqa: E501

    def __init__(self, llm_client: BaseLLMClient):
        """
        Initializes the prompt service.

        Args:
            llm_client: Client for interacting with LLM
        """
        self.llm_client = llm_client
        self.logger = LoggerManager.get_logger(__name__)

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
                raw_prompt = self.llm_client.generate(messages)
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
        """Cleans the prompt from extra characters and meta-instructions."""
        stop_phrases = ["Instruction", "Explanation", "Note", "Ensure", "Remember"]

        for phrase in stop_phrases:
            idx = text.find(phrase)
            if idx != -1:
                text = text[:idx].strip()

        return text.replace("**", "").replace("```", "").strip()

    def _contains_cyrillic(self, text: str) -> bool:
        """Checks for Cyrillic characters."""
        return any("а" <= c.lower() <= "я" for c in text)  # noqa: RUF001

    def _get_fallback_prompt(self, user_text: str, style: MemeStyle) -> str:
        """Returns a fallback prompt in case of errors."""
        return f"A scene depicting: {user_text}, {style.description}"
