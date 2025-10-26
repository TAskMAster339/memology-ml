# 🧠 Memology-ML — Движок для генерации мемов с помощью ИИ

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🇬🇧 English version](README.md)

**Memology-ML** — это основной компонент машинного обучения проекта **Memology**, платформы для генерации мемов с помощью ИИ. Этот модуль создаёт **визуальный контент** и **смешные подписи** используя Stable Diffusion WebUI и Ollama (LLaMA 3.2). Вся обработка происходит **локально**, поэтому ваши мемы создаются **приватно и оффлайн**.

## 🎨 Примеры мемов

| Идея                      | Сгенерированный мем                                    |
| ------------------------- | ------------------------------------------------------ |
| "кот пьет кофе"           | ![Кот пьет кофе](examples/cat_with_coffee_example.png) |
| "лошадь чихнула"          | ![Лошадь чихнула](examples/horse_example.png)          |
| "компьютер и ежу понятен" | ![Компьютер очевиден](examples/computer_example.png)   |

## ✨ Возможности

- 🖼️ **Локальная генерация высокого качества** — Вся обработка происходит на вашем компьютере
- 🎨 **Множество визуальных стилей** — Реализм, аниме, мультяшный стиль, киберпанк, фэнтези и другие
- 🧠 **Умная генерация промптов** — Автоматическое создание английских промптов из русских идей
- 😂 **Остроумные подписи** — Короткие смешные русские подписи, созданные ИИ
- ✍️ **Автоматическое наложение текста** — Профессиональный мемный текст шрифтом Impact
- 📊 **Подробное логирование** — Отслеживание всего процесса генерации
- 🏗️ **Чистая ООП архитектура** — Модульная, тестируемая и расширяемая кодовая база
- ⚙️ **Гибкая конфигурация** — Поддержка переменных окружения и конфигурационных файлов

## 🏗️ Архитектура

Проект следует современным принципам **объектно-ориентированного программирования** с чётким разделением ответственности:

```
memology-ml/
├── src/
│   ├── config/          # Управление конфигурацией
│   ├── core/            # Абстракции для LLM и генерации изображений
│   ├── services/        # Бизнес-логика (промпты, подписи, оркестрация)
│   ├── utils/           # Вспомогательные утилиты (логирование, обработка изображений)
│   └── models/          # Модели данных и структуры
├── tests/               # Юнит-тесты
├── examples/            # Примеры мемов
├── generated_images/    # Директория для результатов
├── main.py             # Точка входа приложения
└── requirements.txt    # Зависимости Python
```

### Ключевые компоненты

- **ConfigManager** — Централизованная конфигурация с поддержкой `.env`
- **LLMClient** — Абстракция для взаимодействия с Ollama
- **ImageGenerator** — Интеграция со Stable Diffusion WebUI
- **PromptService** — Генерация визуальных промптов
- **CaptionService** — Создание подписей для мемов
- **MemeService** — Главный сервис оркестрации
- **ImageUtils** — Манипуляции с изображениями и наложение текста

## 📋 Требования

- **Python** 3.13+
- **Ollama** с моделью LLaMA 3.2
- **Stable Diffusion WebUI** (AUTOMATIC1111)
- **Шрифт Impact** (`impact.ttf`)

## ⚙️ Установка

### 1️⃣ Клонирование репозитория

```bash
git clone https://github.com/TAskMAster339/memology-ml.git
cd memology-ml
```

### 2️⃣ Создание и активация виртуального окружения

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🧠 Настройка Ollama

### Установка Ollama

👉 [https://ollama.com/download](https://ollama.com/download)

### Загрузка модели LLaMA 3.2

```bash
ollama pull llama3.2:3b
```

Проверка установки:

```bash
ollama run llama3.2:3b
```

## 🎨 Настройка Stable Diffusion WebUI

### 1️⃣ Установка WebUI

👉 [https://github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 2️⃣ Запуск WebUI с включенным API

```bash
python launch.py --api
```

Это запустит API по адресу: `http://127.0.0.1:7860/sdapi/v1/txt2img`

### 3️⃣ (Опционально) Добавление пользовательских моделей

Скачайте дополнительные модели с [Civitai](https://civitai.com/):

| Модель           | Стиль                           | Ссылка                                                     |
| ---------------- | ------------------------------- | ---------------------------------------------------------- |
| **Memes XL**     | Мемный стиль, весёлый, яркий    | [Скачать](https://civitai.com/models/205229/memes-xl)      |
| **Crazy Horror** | Тёмный, сюрреалистичный, хоррор | [Скачать](https://civitai.com/models/1101129/crazy-horror) |

Поместите скачанные `.safetensors` файлы в:

```
stable-diffusion-webui/models/Stable-diffusion/
```

## 🔧 Конфигурация

Создайте файл `.env` в корне проекта (см. `.env.example`):

```env
# Конфигурация Ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=15
OLLAMA_BASE_URL=http://localhost:11434

# Конфигурация Stable Diffusion
SD_BASE_URL=http://127.0.0.1:7860
SD_STEPS=20
SD_WIDTH=512
SD_HEIGHT=512
SD_SAMPLER=DPM++ 2M Karras
SD_CFG_SCALE=7.0
SD_RESTORE_FACES=True

# Настройки приложения
OUTPUT_DIR=generated_images
LOG_FILE=generation.log
FONT_PATH=impact.ttf
```

### Параметры конфигурации

| Параметр                 | Описание                        | По умолчанию      |
| ------------------------ | ------------------------------- | ----------------- |
| `OLLAMA_MODEL`           | Название модели LLM             | `llama3.2:3b`     |
| `OLLAMA_TIMEOUT`         | Таймаут запроса к LLM (секунды) | `15`              |
| `SD_STEPS`               | Количество шагов диффузии       | `20`              |
| `SD_WIDTH` / `SD_HEIGHT` | Размеры изображения             | `512x512`         |
| `SD_SAMPLER`             | Метод сэмплирования             | `DPM++ 2M Karras` |
| `SD_CFG_SCALE`           | Сила следования промпту         | `7.0`             |

## 🚀 Использование

### Базовое использование

```bash
python main.py
```

Приложение сгенерирует мемы для предопределённых примеров и сохранит их в `generated_images/`.

### Программное использование

```python
from src.services.meme_service import MemeService
from main import create_meme_service

# Инициализация сервиса
meme_service = create_meme_service()

# Генерация мема
result = meme_service.generate_meme("кот пьет кофе")

if result.success:
    print(f"Мем создан: {result.final_image_path}")
    print(f"Подпись: {result.caption}")
else:
    print(f"Ошибка: {result.error_message}")
```

### Пользовательские стили

```python
from src.models.meme import MemeStyle

# Определение пользовательского стиля
custom_style = MemeStyle(
    name="retro",
    description="ретро стиль 80-х, неоновые цвета, эстетика vaporwave"
)

# Генерация с пользовательским стилем
result = meme_service.generate_meme("кот в космосе", style=custom_style)
```

## 📊 Логирование

Каждая генерация логируется в `generation.log`:

```
2025-10-26 23:56:10 | src.services.meme_service | INFO | Starting meme generation: 9e0bbf0f
2025-10-26 23:56:22 | src.services.prompt_service | INFO | Generated prompt: A cat drinking coffee...
2025-10-26 23:56:24 | src.services.caption_service | INFO | Generated caption: Кот просто не умеет
2025-10-26 23:58:24 | src.services.meme_service | INFO | Meme generation completed in 134.12s
```

## 🧪 Тестирование

Запуск юнит-тестов:

```bash
python -m pytest tests/
```

## 🛠️ Разработка

### Философия структуры проекта

Проект следует **принципам SOLID** и чистой архитектуре:

- **Single Responsibility** — Каждый класс имеет одну чёткую цель
- **Open/Closed** — Открыт для расширения, закрыт для модификации
- **Dependency Injection** — Зависимости передаются через конструкторы
- **Separation of Concerns** — Бизнес-логика отделена от инфраструктуры

### Добавление новых возможностей

**Пример: Добавление нового провайдера LLM**

1. Создайте новый класс в `src/core/llm_client.py`:

```python
class OpenAIClient(BaseLLMClient):
    def generate(self, messages, timeout=None):
        # Реализация
        pass
```

2. Обновите `main.py` для использования нового клиента:

```python
llm_client = OpenAIClient(api_key=config.openai_api_key)
```

**Пример: Добавление нового стиля изображения**

1. Добавьте в `src/models/meme.py`:

```python
PREDEFINED_STYLES.append(
    MemeStyle("steampunk", "стимпанк, Викторианская эра, латунь и медь")
)
```

## 📝 Документация API

### MemeService

**`generate_meme(user_input: str, style: Optional[MemeStyle] = None) -> MemeGenerationResult`**

Генерирует мем из пользовательского ввода.

- **Параметры:**
  - `user_input` — Идея мема на русском языке
  - `style` — Визуальный стиль (случайный, если None)
- **Возвращает:** `MemeGenerationResult` с путями и метаданными

### PromptService

**`generate_visual_prompt(user_text: str, style: MemeStyle, max_retries: int = 1) -> str`**

Создаёт английский визуальный промпт для генерации изображения.

### CaptionService

**`generate_caption(scene_description: str) -> str`**

Генерирует короткую смешную русскую подпись.

## 🤝 Участие в разработке

Мы приветствуем ваш вклад! Вот как вы можете помочь:

1. Сделайте форк репозитория
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Внесите изменения, следуя структуре проекта
4. Добавьте тесты для новой функциональности
5. Запустите тесты: `pytest tests/`
6. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
7. Отправьте в ветку (`git push origin feature/amazing-feature`)
8. Откройте Pull Request

### Стиль кода

- Следуйте рекомендациям PEP 8
- Используйте type hints
- Добавляйте docstrings к публичным методам
- Держите классы сфокусированными и небольшими

## 💡 Советы и оптимизация

- **Более быстрая генерация:** Уменьшите `SD_STEPS` до `10-15`
- **Лучшее качество:** Используйте модели SDXL или увеличьте steps до `30-40`
- **Тёмные мемы:** Попробуйте модель "Crazy Horror"
- **Аниме стиль:** Используйте модель "Anything V5"
- **Всё работает оффлайн** — API ключи не требуются!

## 🐛 Решение проблем

### Частые проблемы

**Проблема:** `ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=7860)`

**Решение:**

- Убедитесь, что Stable Diffusion WebUI запущен с флагом `--api`
- Проверьте, что WebUI доступен по адресу http://127.0.0.1:7860

**Проблема:** `ConnectionRefusedError` для Ollama

**Решение:**

- Запустите Ollama: `ollama serve`
- Проверьте, что модель установлена: `ollama list`

**Проблема:** Текст не помещается на изображении

**Решение:**

- Отсутствует файл шрифта — убедитесь, что `impact.ttf` существует
- Уменьшите длину подписи в промпте

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [Ollama](https://ollama.com/) — Локальная среда выполнения LLM
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) — Stable Diffusion WebUI
- [Stability AI](https://stability.ai/) — Модель Stable Diffusion

## 📬 Контакты

Ссылка на проект: [https://github.com/TAskMAster339/memology-ml](https://github.com/TAskMAster339/memology-ml)

---

**Создано с ❤️ и ИИ** | Для любителей мемов и практиков машинного обучения
