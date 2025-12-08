import json
import random
import re

from src.config.logging_config import get_logger
from src.services.caption_service import CaptionForImageService
from src.templates.memes import DEFAULT_HEIGHT, DEFAULT_WIDTH, MEME_TEMPLATES_DATABASE


class MemeGenerator:
    """Генератор мемов с использованием memegen.link и LLM"""

    BASE_URL = "https://api.memegen.link"
    ANSWER_LEN = 40

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        caption_service: CaptionForImageService = None,
    ):
        self.ollama_url = ollama_url
        self.caption_service = caption_service
        self.logger = get_logger(__name__)

    def select_random_template(self) -> dict:
        """Выбирает случайный шаблон из всех 105"""
        template = random.choice(MEME_TEMPLATES_DATABASE)

        self.logger.info(f"Выбран шаблон: {template['id']}")  # noqa: G004

        return template

    def generate_captions_with_llm(
        self,
        context: str,
        template: dict,
    ) -> list[str]:
        """
        Генерирует подписи для мема с помощью LLM.

        Args:
            context: Контекст от пользователя.
            template_id: ID шаблона (например, 'drake').

        Returns:
            list[str]
        """
        num_lines = template.get("lines", 2)
        prompt = f"""
            Шаблон - {template["template"]}
            Контекст пользователя - {context}
            Возвращай ровно {num_lines} строк как JSON список.
            Пример:
            ["Первая строка", "Вторая строка"]
            """

        try:
            captions = self.caption_service.generate_caption(prompt.strip())

            return self.parse_llm_lines(captions)
        except Exception as e:
            self.logger.error(f"Ошибка генерации LLM: {e}")  # noqa: G004

        return self._fallback_generation(context, template["id"])

    def parse_llm_lines(self, response: str) -> list[str]:
        """Безопасно парсит JSON от LLM с обработкой сложных случаев."""

        def clean_response(text: str) -> str:
            """Очищает ответ от мусора вокруг JSON."""
            text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)

            text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)

            text = re.sub(
                r"^json\s*:?\s*",
                "",
                text,
                flags=re.IGNORECASE | re.MULTILINE,
            )

            return text.strip()

        # 1. Очищаем ответ
        cleaned = clean_response(response)

        # 2. Пробуем стандартный парсинг
        try:
            result = json.loads(cleaned)
            if isinstance(result, list):
                return [str(line).strip() for line in result]
        except json.JSONDecodeError:
            pass

        # 3. Ищем JSON внутри текста (если есть мусор)
        json_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                if isinstance(result, list):
                    return [str(line).strip() for line in result]
            except json.JSONDecodeError:
                pass

        # 4. Пробуем заменить одинарные кавычки на двойные (популярная ошибка LLM)
        fixed_quotes = cleaned.replace("'", '"')
        try:
            result = json.loads(fixed_quotes)
            if isinstance(result, list):
                return [str(line).strip() for line in result]
        except json.JSONDecodeError:
            pass

        # 5. Fallback: извлекаем строки между кавычками
        strings = re.findall(r'"(.*?)"', cleaned)
        if strings:
            return [s.strip() for s in strings[:10]]  # Лимит на 10 строк

        # 6. Финальный fallback: по новым строкам
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        return lines if lines else []

    def _fallback_generation(self, context: str, template_id: str) -> list[str]:
        """Простая генерация без LLM (фоллбэк)."""

        if template_id == "buzz":
            words = context.split()
            noun = words[0] if words else "Это"
            return [noun, f"{noun} повсюду 🌍"]

        if template_id == "fine":
            top = context[:40] + "..." if len(context) > 40 else context
            return [top, "Всё хорошо ☕"]

        if template_id == "stonks":
            return [context[:40], "STONKS 📈"]

        if template_id == "rollsafe":
            return [
                "Нельзя иметь проблемы\nЕсли их игнорировать",
                "",
            ]

        # Дефолтный случай: разделяем текст пополам
        words = context.split()
        mid = len(words) // 2
        return [
            " ".join(words[:mid]) or context,
            " ".join(words[mid:]) or "",
        ]

    def encode_text(self, text: str) -> str:
        """
        Кодирует текст для URL по правилам memegen

        Правила:
        - пробел → _ (underscore)
        - _ → __ (два underscore)
        - - → -- (два дефиса)
        - перенос строки → ~n
        - ? → ~q
        - & → ~a
        - % → ~p
        - # → ~h
        - / → ~s
        - \ → ~b
        """  # noqa: W605
        if not text:
            return "_"

        # Экранируем служебные символы
        text = text.replace("_", "__")
        text = text.replace("-", "--")
        text = text.replace("?", "~q")
        text = text.replace("&", "~a")
        text = text.replace("%", "~p")
        text = text.replace("#", "~h")
        text = text.replace("/", "~s")
        text = text.replace("\\", "~b")

        # Заменяем пробелы и переносы
        text = text.replace(" ", "_")
        return text.replace("\n", "~n")

    def generate_meme_url(
        self,
        template: dict,
        text_list: list[str],
        font: str = "notosans",
        width: int | None = None,
        height: int | None = None,
    ) -> str:
        """Формирует URL мема"""
        encoded_text = [self.encode_text(text) for text in text_list]
        n = len(encoded_text)
        url = [self.BASE_URL, "images", template["id"]]

        for i in range(n):
            if i + 1 == n:
                text = encoded_text[i] + ".png"
                url.append(text)
                break
            url.append(encoded_text[i])
            print(url)
        url = "/".join(url)

        print(encoded_text)

        params = []
        if font:
            params.append(f"font={font}")
        if width and width != DEFAULT_WIDTH:
            params.append(f"width={width}")
        if height and height != DEFAULT_HEIGHT:
            params.append(f"height={height}")

        if params:
            url += "?" + "&".join(params)

        self.logger.info(f"Generated URL: {url}")  # noqa: G004

        return url

    def generate_meme(
        self,
        context: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
    ) -> dict:
        """
        Генерирует мем со случайным шаблоном

        Args:
            context: Контекст от пользователя
            width: Ширина мема
            height: Высота мема

        Returns:
            dict: {
                'url': str,
                'template': str,
                'top_text': str,
                'bottom_text': str,
                'template_instruction': str
            }
        """

        # 1. Выбираем случайный шаблон
        template = self.select_random_template()

        # 2. Генерируем подписи с LLM  # noqa: RUF003
        captions = self.generate_captions_with_llm(
            context=context,
            template=template,
        )
        # 3. Формируем URL мема
        meme_url = self.generate_meme_url(
            template=template,
            text_list=captions,
            font="notosans",  # Поддержка кириллицы
            width=width,
            height=height,
        )

        return {
            "url": meme_url,
            "template": template["id"],
            "text": str(captions),
        }
