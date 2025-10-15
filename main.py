import base64
import logging
import os
import random
import textwrap
import threading
import time
from datetime import datetime
from io import BytesIO
from uuid import uuid4

import ollama
import requests
from PIL import Image, ImageDraw, ImageFont

# === НАСТРОЙКИ ===
MODEL = "llama3.2:3b"
OUTPUT_DIR = "generated_images"
LOG_FILE = "generation.log"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === ЛОГИРОВАНИЕ ===
logger = logging.getLogger("meme_generator")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# === ПРОМПТЫ ===
PROMPT_GENERATOR_SYSTEM = """
You are a professional prompt engineer for Stable Diffusion and your task is to create a single high-quality English text description of an image.

Requirements:
- Output only the prompt text — one paragraph, no formatting, no quotes, no explanations.
- The style must be visually rich and cinematic.
- Include details about lighting, mood, color palette, and depth of field.
- Use realistic or artistic rendering styles such as:
  "ultra realistic", "studio lighting", "anime style", "cinematic lighting", "digital art", "hyperdetailed", "4k render".
- Adapt the style to match the topic:
   - use "anime style" or "cartoon" for fun, lighthearted, or cute topics;
   - use "realistic", "cinematic lighting" for serious, dramatic, or lifelike ideas.
- Mention a suitable camera angle (e.g., “close-up”, “wide shot”, “from above”, “portrait”, etc.) when relevant.
- Never use markdown, colons, explanations, or any meta instructions.
- The text should be directly usable as a Stable Diffusion prompt.

Example topics and how to respond:
User: "cat drinking coffee"
Output: "a fluffy cat with round cheeks sitting at a cozy table, holding a steaming coffee cup, warm morning sunlight, cinematic lighting, ultra realistic, 4k render, depth of field"
"""


CAPTION_GENERATOR_SYSTEM = """
Ты — генератор коротких мемных подписей.
Создавай короткие смешные подписи на русском языке (2–4 слов).
Используй сарказм, самоиронию, иронию или жизненные ситуации.
Не упоминай людей, бренды, политику и не используй грубости.
Отвечай только подписью, без кавычек и пояснений.
"""

STYLES = [
    "anime style, vibrant colors, soft lighting, detailed, 4k render",
    "ultra realistic, cinematic lighting, shallow depth of field, photo style, HDR, 8k",
    "cartoon style, exaggerated expressions, colorful, flat shading, digital illustration",
    "cyberpunk, neon lights, futuristic atmosphere, dark streets, glowing reflections",
    "fantasy art, mystical lighting, ethereal glow, highly detailed, magical realism",
    "oil painting, baroque composition, dramatic shadows, rich colors, textured brushstrokes",
    "watercolor art, pastel tones, dreamy mood, soft contrast",
    "pixel art, retro video game vibe, limited palette, crisp edges",
]


# === УТИЛИТЫ ===
def run_with_timeout(func, timeout, *args, **kwargs):
    """Запускает функцию с ограничением по времени."""
    result = [None]
    thread = threading.Thread(
        target=lambda: result.__setitem__(0, func(*args, **kwargs)),
    )
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutError(
            f"Время выполнения функции {func.__name__} превышено ({timeout} сек)",
        )
    return result[0]


def get_random_style():
    """Возвращает случайный художественный стиль из списка."""
    return random.choice(STYLES)  # noqa: S311


def clean_prompt(text: str) -> str:
    """Удаляет лишние куски и технические вставки."""
    stop_phrases = ["Instruction", "Explanation", "Note", "Ensure", "Remember"]
    for phrase in stop_phrases:
        idx = text.find(phrase)
        if idx != -1:
            text = text[:idx].strip()
    return text.replace("**", "").replace("```", "").strip()


# === LLM ===
def generate_visual_prompt(user_text: str, retries=1):
    """Создаёт англоязычный промпт для изображения."""
    try:
        style = get_random_style()
        response = run_with_timeout(
            ollama.chat,
            15,
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT_GENERATOR_SYSTEM},
                {
                    "role": "user",
                    "content": f"Describe this scene in English: {user_text}. Style: {style}.",
                },
            ],
        )
        raw = clean_prompt(response["message"]["content"])
        # Проверяем, есть ли кириллица
        if any("а" <= c.lower() <= "я" for c in raw):
            if retries > 0:
                logger.warning(
                    "⚠️ Промпт на русском, повторная попытка с уточнением языка.",
                )
                return generate_visual_prompt(
                    f"{user_text}. Answer ONLY in English.",
                    retries - 1,
                )
            logger.warning(
                "❌ Модель снова ответила не на английском, оставляем как есть.",
            )
        else:
            return raw
    except TimeoutError as e:
        logger.error(f"⏱️ Таймаут при генерации промпта: {e}")
        return "A funny cat sitting at a table, holding a cup of coffee, cinematic lighting."


def generate_caption(scene_description: str):
    """Создаёт короткую подпись на русском."""
    try:
        response = run_with_timeout(
            ollama.chat,
            10,
            model=MODEL,
            messages=[
                {"role": "system", "content": CAPTION_GENERATOR_SYSTEM},
                {"role": "user", "content": scene_description},
            ],
        )
        text = clean_prompt(response["message"]["content"])
        return text.split("\n")[0][:80]
    except TimeoutError as e:
        logger.error(f"⏱️ Таймаут при генерации подписи: {e}")
        return "Когда кофе не помогает"


# === ИЗОБРАЖЕНИЕ ===
def generate_image(prompt):
    # Параметры оптимизированы под скорость и качество
    payload = {
        "prompt": prompt,
        "steps": 20,  # достаточно для деталей, но не слишком долго
        "width": 512,  # быстрое разрешение
        "height": 512,
        "sampler_index": "DPM++ 2M Karras",  # сбалансированный по скорости/качеству
        "cfg_scale": 7,  # насколько строго следовать промпту
        "restore_faces": True,  # если есть лица — улучшает
        "batch_size": 1,
        "n_iter": 1,
        "seed": -1,  # случайный сид для разнообразия
        "negative_prompt": (
            "low quality, blurry, bad anatomy, distorted, extra limbs, "
            "poorly drawn, text, watermark, signature, logo"
        ),
        # "model": "v1-5-pruned-emaonly",  # 👈 указываем нужную модель
    }
    r = requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
    image_base64 = r.json()["images"][0]
    image = Image.open(BytesIO(base64.b64decode(image_base64)))

    filename = (
        f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}_raw.png"
    )
    path = os.path.join(OUTPUT_DIR, filename)
    image.save(path)
    return path


# === CAPTION DRAWING ===
def add_caption(image_path, text):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    font_path = "impact.ttf"
    # начальный размер шрифта — примерно 10% от высоты изображения
    font_size = int(image.height * 0.1)
    max_width = int(image.width * 0.95)
    max_height = int(image.height * 0.35)

    # функция для вычисления размеров текста
    def get_text_size(lines, font):
        total_height = 0
        max_line_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            total_height += h + 5
            max_line_width = max(max_line_width, w)
        return max_line_width, total_height

    # уменьшаем шрифт, пока всё не влезет
    while font_size > 16:
        font = ImageFont.truetype(font_path, font_size)
        # ширину wrap подбираем динамически
        wrap_width = max(8, int(image.width / (font_size * 0.6)))
        lines = textwrap.wrap(text, width=wrap_width)
        text_w, text_h = get_text_size(lines, font)
        if text_w <= max_width and text_h <= max_height:
            break
        font_size -= 2

    # вычисляем начальную позицию (чуть выше нижнего края)
    y = image.height - text_h - int(image.height * 0.03)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (image.width - w) / 2

        # обводка (черный контур)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), line, font=font, fill="black")

        # основной текст (белый)
        draw.text((x, y), line, font=font, fill="white")
        y += h + 5

    # сохраняем итоговую картинку
    filename = (
        f"meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}_final.png"
    )
    output_path = os.path.join(OUTPUT_DIR, filename)
    image.save(output_path)
    return output_path


# === PIPELINE ===
def main():
    # user_input = input("\n💡 Введите идею для мема: ").strip()
    user_input = """
    Компьютер и ежу понятен"""
    if not user_input:
        print("⚠️ Идея не введена, завершение работы.")
        return

    start_time = time.time()
    print("\n🧠 Генерация промпта...")
    visual_prompt = generate_visual_prompt(
        f"{user_input}. Style: anime style, vibrant colors, detailed, 4k render",
    )
    print("🎨 Промпт:", visual_prompt)

    print("\n🖼️ Генерация изображения через Stable Diffusion...")
    image_path = generate_image(visual_prompt)

    print("\n😂 Генерация подписи для мема...")
    caption = generate_caption(user_input)
    print("💬 Подпись:", caption)

    print("\n✍️ Наносим подпись...")
    final_path = add_caption(image_path, caption)

    elapsed = round(time.time() - start_time, 2)
    logger.info(
        f"Model: {MODEL} | Prompt: {user_input.replace('\n', ' ').strip()} | "
        f"Visual: {visual_prompt} | Caption: {caption} | "
        f"RawFile: {os.path.basename(image_path)} | FinalFile: {os.path.basename(final_path)} | Time: {elapsed}s"
    )

    print(f"\n✅ Мем готов: {final_path}")
    print(f"🕒 Время генерации: {elapsed} сек")
    print(f"📁 Лог записан в {LOG_FILE}")


if __name__ == "__main__":
    for _ in range(10):
        main()
