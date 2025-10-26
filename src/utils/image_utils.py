"""
Utilities for working with images: adding text, saving, etc.
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.utils.logger import LoggerManager


class ImageUtils:
    """Utilities for image manipulations."""

    def __init__(self, font_path: str = "impact.ttf"):
        """
        Initializes the utilities.

        Args:
            font_path: Path to the font file
        """
        self.font_path = font_path
        self.logger = LoggerManager.get_logger(__name__)

    def add_caption_to_image(
        self,
        image: Image.Image,
        caption: str,
        max_font_size: int | None = None,
    ) -> Image.Image:
        """
        Adds a caption to the image in meme style.

        Args:
            image: Source image
            caption: Caption text
            max_font_size: Maximum font size (None = auto)

        Returns:
            Image with caption
        """
        self.logger.info(f"Adding caption to image: {caption}")  # noqa: G004

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        draw = ImageDraw.Draw(image)

        # Initial font size
        font_size = int(image.height * 0.1) if max_font_size is None else max_font_size

        # Size constraints
        max_width = int(image.width * 0.95)
        max_height = int(image.height * 0.35)

        # Select font size
        font, lines = self._fit_text(caption, font_size, max_width, max_height, draw)

        # Calculate position (at the bottom of the image)
        text_height = self._calculate_text_height(lines, font, draw)
        y_position = image.height - text_height - int(image.height * 0.03)

        # Draw text with outline
        self._draw_text_with_outline(draw, lines, font, y_position, image.width)

        return image

    def _fit_text(  # noqa: PLR0913
        self,
        text: str,
        initial_font_size: int,
        max_width: int,
        max_height: int,
        draw: ImageDraw.Draw,
        min_font_size: int = 16,
    ) -> tuple[ImageFont.FreeTypeFont, list]:
        """
        Selects font size and line breaks for the text.

        Args:
            text: Text to place
            initial_font_size: Initial font size
            max_width: Maximum width of the area
            max_height: Maximum height of the area
            draw: ImageDraw object for measurements
            min_font_size: Minimum font size

        Returns:
            Tuple (font, list of lines)
        """
        font_size = initial_font_size

        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except OSError:
                self.logger.warning(f"Font not found: {self.font_path}, using default")  # noqa: G004
                font = ImageFont.load_default()

            # Calculate wrap width
            wrap_width = max(8, int(max_width / (font_size * 0.6)))
            lines = textwrap.wrap(text, width=wrap_width)

            # Check sizes
            text_width = max(
                draw.textbbox((0, 0), line, font=font)[2] for line in lines
            )
            text_height = self._calculate_text_height(lines, font, draw)

            if text_width <= max_width and text_height <= max_height:
                return font, lines

            font_size -= 2

        # If unable to fit, return minimum size
        try:
            font = ImageFont.truetype(self.font_path, min_font_size)
        except OSError:
            font = ImageFont.load_default()

        wrap_width = max(8, int(max_width / (min_font_size * 0.6)))
        lines = textwrap.wrap(text, width=wrap_width)

        return font, lines

    def _calculate_text_height(
        self,
        lines: list,
        font: ImageFont.FreeTypeFont,
        draw: ImageDraw.Draw,
    ) -> int:
        """Calculates the total height of the text."""
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            total_height += line_height + 5  # 5px between lines
        return total_height

    def _draw_text_with_outline(  # noqa: PLR0913
        self,
        draw: ImageDraw.Draw,
        lines: list,
        font: ImageFont.FreeTypeFont,
        y_start: int,
        image_width: int,
        outline_width: int = 3,
    ):
        """
        Draws text with a black outline (meme style).

        Args:
            draw: Drawing object
            lines: List of text lines
            font: Font
            y_start: Starting Y coordinate
            image_width: Image width
            outline_width: Outline thickness
        """
        y = y_start

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]

            # Center horizontally
            x = (image_width - line_width) / 2

            # Draw black outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (x + dx, y + dy),
                            line,
                            font=font,
                            fill="black",
                        )

            # Draw white text on top
            draw.text((x, y), line, font=font, fill="white")
            y += line_height + 5

    def save_image(
        self,
        image: Image.Image,
        output_path: str,
        quality: int = 95,
    ) -> str:
        """
        Saves the image to a file.

        Args:
            image: Image to save
            output_path: Path to save
            quality: JPEG quality (1-100)

        Returns:
            Absolute path to the saved file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        image.save(str(path), quality=quality)
        self.logger.info(f"Image saved to: {path.absolute()}")  # noqa: G004

        return str(path.absolute())
