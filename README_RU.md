# 🧠 Memology-ML — Движок для генерации мемов на основе ИИ

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🇬🇧 English Version](README.md)

**Memology-ML** — это основной компонент машинного обучения проекта **Memology**, платформы для генерации мемов на основе ИИ. Этот модуль создаёт **визуальное содержимое мемов** и **забавные подписи** с использованием Stable Diffusion WebUI и Ollama (LLaMA 3.2). Вся обработка выполняется **локально**, поэтому ваши мемы создаются **приватно и офлайн**.

## 📋 Содержание

- [Примеры мемов](#-примеры-мемов)
- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Требования](#-требования)
- [Установка](#-установка)
- [Настройка](#-настройка)
  - [Настройка Ollama](#-настройка-ollama)
  - [Настройка Stable Diffusion WebUI](#-настройка-stable-diffusion-webui)
  - [Настройка Docker (рекомендуется)](#-настройка-docker-рекомендуется)
- [Конфигурация](#-конфигурация)
- [Использование](#-использование)
- [Документация API](#-документация-api)
- [Тестирование](#-тестирование)
- [Разработка](#-разработка)
- [Руководство Docker](#-руководство-docker)
- [Устранение неполадок](#-устранение-неполадок)
- [Советы и оптимизация](#-советы-и-оптимизация)
- [Внесение вклада](#-внесение-вклада)

## 🎨 Примеры мемов

| Идея для мема                       | Сгенерированный мем                                       |
| ----------------------------------- | --------------------------------------------------------- |
| [translate:кот пьет кофе]           | ![Кот пьет кофе](examples/cat_with_coffee_example.png)    |
| [translate:лошадь чихнула]          | ![Лошадь чихнула](examples/horse_example.png)             |
| [translate:компьютер и ежу понятен] | ![Компьютер и ежу понятен](examples/computer_example.png) |

## ✨ Возможности

- 🖼️ **Высокое качество локальной генерации** — Вся обработка происходит на вашем компьютере
- 🎨 **Множество визуальных стилей** — Реалистичный, аниме, мультяшный, киберпанк, фэнтези и другие
- 🧠 **Умное инженирование подсказок** — Автоматическое преобразование русских идей в английские подсказки
- 😂 **Смешные подписи** — Короткие смешные русские подписи, созданные ИИ
- ✍️ **Автоматическое наложение текста** — Профессиональный мем-стиль текста со шрифтом Impact
- 📊 **Полное логирование** — Отслеживание полного процесса генерации
- 🏗️ **Чистая OOP архитектура** — Модульный, тестируемый и расширяемый код
- ⚙️ **Гибкая конфигурация** — Поддержка переменных окружения и файлов конфигурации
- 🐳 **Поддержка Docker** — Локальный запуск или в контейнерах со всеми зависимостями
- 🚀 **Интеграция FastAPI** — REST API для генерации мемов
- 📈 **Масштабируемость** — Поддержка нескольких экземпляров сервиса

## 🏗️ Архитектура

Проект следует принципам современного **объектно-ориентированного программирования** с четким разделением ответственности:

```
memology-ml/
├── src/
│   ├── config/          # Управление конфигурацией
│   ├── core/            # Абстракции для LLM и генерации изображений
│   ├── services/        # Бизнес-логика (подсказки, подписи, оркестрация)
│   ├── utils/           # Вспомогательные утилиты (логирование, обработка изображений)
│   └── models/          # Модели данных и структуры
├── tests/               # Модульные тесты
├── examples/            # Примеры мемов
├── generated_images/    # Директория для вывода
├── docker-compose.yml   # Конфигурация Docker Compose
├── Dockerfile          # Docker образ для API сервиса
├── Dockerfile.ollama   # Docker образ для ollama
├── main.py             # Точка входа приложения
├── requirements.txt    # Зависимости Python
└── README.md          # Этот файл
```

### Ключевые компоненты

- **ConfigManager** — Централизованная конфигурация с поддержкой `.env`
- **LLMClient** — Абстракция для взаимодействия с Ollama
- **ImageGenerator** — Интеграция Stable Diffusion WebUI
- **PromptService** — Генерация визуальных подсказок
- **CaptionService** — Создание подписей к мемам
- **MemeService** — Основной сервис оркестрации
- **ImageUtils** — Манипуляция изображениями и наложение текста

## 📦 Требования

### Для локальной разработки:

- **Python** 3.13+
- **Ollama** с моделью LLaMA 3.2
- **Stable Diffusion WebUI** (AUTOMATIC1111)
- **Шрифт Impact** (`impact.ttf`)

### Для Docker:

- Docker Engine 20.10+
- Docker Compose 2.0+
- Минимум 8 GB RAM (16 GB рекомендуется для ML моделей)
- NVIDIA GPU (опционально, для ускорения)

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

## 🧠 Настройка

### 🦙 Настройка Ollama

#### Установка Ollama

👉 [https://ollama.com/download](https://ollama.com/download)

#### Загрузка модели LLaMA 3.2

```bash
ollama pull llama3.2:3b
```

Проверка установки:

```bash
ollama run llama3.2:3b
```

Ollama будет доступна по адресу: `http://localhost:11434`

### 🎨 Настройка Stable Diffusion WebUI

#### 1️⃣ Установка WebUI

👉 [https://github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

#### 2️⃣ Запуск WebUI с включённым API

```bash
python launch.py --api
```

Это запустит API по адресу: `http://127.0.0.1:7860/sdapi/v1/txt2img`

#### 3️⃣ (Опционально) Добавление пользовательских моделей

Загрузите дополнительные модели с [Civitai](https://civitai.com/):

| Модель           | Стиль                     | Ссылка                                                       |
| ---------------- | ------------------------- | ------------------------------------------------------------ |
| **Memes XL**     | Мем-стиль, смешной, яркий | [Загрузить](https://civitai.com/models/205229/memes-xl)      |
| **Crazy Horror** | Тёмный, сюрреальный, ужас | [Загрузить](https://civitai.com/models/1101129/crazy-horror) |

Поместите загруженные файлы `.safetensors` в:

```
stable-diffusion-webui/models/Stable-diffusion/
```

### 🐳 Настройка Docker (рекомендуется)

Docker Compose позволяет запустить все сервисы в изолированных контейнерах с согласованными окружениями.

#### 1️⃣ Конфигурация переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте файл `.env` согласно вашим требованиям:

```env
# Конфигурация API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Конфигурация модели
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_TIMEOUT=15

# Конфигурация Stable Diffusion
SD_BASE_URL=http://sd-webui:7860
SD_STEPS=20
SD_WIDTH=512
SD_HEIGHT=512
SD_SAMPLER=DPM++ 2M Karras
SD_CFG_SCALE=7.0

# Параметры приложения
OUTPUT_DIR=generated_images
LOG_FILE=generation.log
FONT_PATH=impact.ttf
```

#### 2️⃣ Запуск всех сервисов

```bash
docker compose up -d
```

Эта команда запустит все сервисы, определенные в `docker-compose.yml`:

- **API Service**: доступен по адресу `http://localhost:8000`
- **Swagger UI**: доступен по адресу `http://localhost:8000/docs`
- **Ollama Service**: доступен по адресу `http://localhost:11434`
- **Stable Diffusion WebUI**: доступен по адресу `http://localhost:7860`

#### 3️⃣ Проверка статуса сервисов

```bash
# Посмотреть запущенные контейнеры
docker compose ps

# Посмотреть логи всех сервисов
docker compose logs -f

# Посмотреть логи конкретного сервиса
docker compose logs -f api
```

#### 4️⃣ Остановка сервисов

```bash
# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (БД и модели)
docker compose down -v
```

### Порты и URL приложений

| Сервис           | Порт  | URL                          | Описание                        |
| ---------------- | ----- | ---------------------------- | ------------------------------- |
| API Service      | 8000  | http://localhost:8000        | Основной API сервис             |
| Swagger UI       | 8000  | http://localhost:8000/docs   | Интерактивная документация API  |
| ReDoc            | 8000  | http://localhost:8000/redoc  | Альтернативная документация API |
| Health Check     | 8000  | http://localhost:8000/health | Проверка состояния API          |
| Ollama Service   | 11434 | http://localhost:11434       | Сервис LLM моделей              |
| Stable Diffusion | 7860  | http://localhost:7860        | WebUI для генерации изображений |

## ⚙️ Конфигурация

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

# Параметры приложения
OUTPUT_DIR=generated_images
LOG_FILE=generation.log
FONT_PATH=impact.ttf
```

### Параметры конфигурации

| Параметр                 | Описание                      | По умолчанию      |
| ------------------------ | ----------------------------- | ----------------- |
| `OLLAMA_MODEL`           | Название LLM модели           | `llama3.2:3b`     |
| `OLLAMA_TIMEOUT`         | Таймаут LLM запроса (секунды) | `15`              |
| `SD_STEPS`               | Количество шагов диффузии     | `20`              |
| `SD_WIDTH` / `SD_HEIGHT` | Размеры изображения           | `512x512`         |
| `SD_SAMPLER`             | Метод сэмплирования           | `DPM++ 2M Karras` |
| `SD_CFG_SCALE`           | Сила соответствия подсказке   | `7.0`             |

## 🚀 Использование

### Базовое использование (локально)

```bash
python main.py
```

Приложение создаст мемы для предопределённых примеров и сохранит их в `generated_images/`.

### Использование Docker

Генерируйте мемы через FastAPI:

```bash
# Запуск сервисов
docker compose up -d

# Откройте Swagger UI
# http://localhost:8000/docs в браузере

# Генерируйте мем через API
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Кот пьет кофе",
    "style": "realistic"
  }'
```

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
    description="ретро стиль 80-х, неоновые цвета, эстетика вейпорвейв"
)

# Генерация с пользовательским стилем
result = meme_service.generate_meme("кот в космосе", style=custom_style)
```

## 📊 Логирование

Каждая генерация логируется в `logs/`:

```
2025-10-26 23:56:10 | src.services.meme_service | INFO | Начало генерации мема: 9e0bbf0f
2025-10-26 23:56:22 | src.services.prompt_service | INFO | Подсказка сгенерирована: A cat drinking coffee...
2025-10-26 23:56:24 | src.services.caption_service | INFO | Подпись сгенерирована: Кот просто не умеет
2025-10-26 23:58:24 | src.services.meme_service | INFO | Генерация мема завершена за 134.12s
```

## 📚 Документация API

### FastAPI endpoints

После запуска с Docker, документация API доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### Проверка здоровья

```bash
curl http://localhost:8000/health
```

#### Генерация мема

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a meme about programming",
    "style": "classic"
  }'
```

### MemeService

**`generate_meme(user_input: str, style: Optional[MemeStyle] = None) -> MemeGenerationResult`**

Генерирует мем из пользовательского ввода.

- **Параметры:**
  - `user_input` — Идея мема на русском языке
  - `style` — Визуальный стиль (случайный, если не указан)
- **Возвращает:** `MemeGenerationResult` с путями и метаданными

### PromptService

**`generate_visual_prompt(user_text: str, style: MemeStyle, max_retries: int = 1) -> str`**

Создаёт английскую визуальную подсказку для генерации изображения.

### CaptionService

**`generate_caption(scene_description: str) -> str`**

Генерирует короткую смешную русскую подпись.

## 🧪 Тестирование

Запуск модульных тестов:

```bash
python -m pytest tests/
```

## 🛠️ Разработка

### Философия структуры проекта

Проект следует принципам **SOLID** и чистой архитектуре:

- **Single Responsibility** — Каждый класс имеет одну четкую цель
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
    MemeStyle("steampunk", "steampunk art, Victorian era, brass and copper")
)
```

### Обновление зависимостей

```bash
# Обновить requirements.txt
pip freeze > requirements.txt

# Пересобрать Docker образ
docker compose build
```

### Проверка качества кода

```bash
# Линтинг
flake8 app/
black app/ --check
mypy app/

# Форматирование
black app/
isort app/
```

## 🐳 Руководство Docker

### Конфигурация Docker Compose

Проект использует Docker Compose для оркестрации сервисов. Основные файлы:

- `docker-compose.yml` — основная конфигурация
- `Dockerfile` — образ для API сервиса

#### Запуск с production конфигурацией:

```bash
docker compose up -d
```

#### Запуск с development конфигурацией:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Масштабирование сервисов

Docker Compose позволяет масштабировать сервисы:

```bash
# Запуск нескольких экземпляров API
docker compose up -d --scale api=3
```

### Использование GPU

Для использования GPU добавьте в `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

### Логирование и отладка

```bash
# Просмотр логов в реальном времени
docker compose logs -f api

# Вход в контейнер для отладки
docker compose exec api bash

# Просмотр использования ресурсов
docker stats
```

### Очистка Docker ресурсов

```bash
# Удалить неиспользуемые образы, контейнеры и volumes
docker system prune -a --volumes

# Удалить все данные проекта
docker compose down -v
rm -rf .docker-data/
```

## 🐛 Устранение неполадок

### Распространенные проблемы

**Проблема:** `ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=7860)`

**Решение:**

- Убедитесь, что Stable Diffusion WebUI запущена с флагом `--api`
- Проверьте, доступна ли WebUI по адресу [http://127.0.0.1:7860](http://127.0.0.1:7860)

**Проблема:** `ConnectionRefusedError` для Ollama

**Решение:**

- Запустите Ollama: `ollama serve`
- Проверьте установку модели: `ollama list`
- Убедитесь, что Ollama запущена на порте 11434

**Проблема:** Текст не помещается на изображение

**Решение:**

- Отсутствует файл шрифта — убедитесь, что `impact.ttf` существует
- Уменьшите длину подписи в подсказке

**Проблема:** Контейнер не запускается

```bash
# Проверить логи
docker compose logs api

# Проверить статус контейнеров
docker compose ps
```

**Проблема:** Модель не загружается в Docker

```bash
# Проверить доступность сервиса Ollama
curl http://localhost:11434/api/tags

# Перезапустить сервис модели
docker compose restart ollama
```

**Проблема:** Порт уже занят

Измените порты в файле `.env` или `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8080:8000" # Изменить внешний порт
```

**Проблема:** Недостаточно памяти

Увеличьте лимиты в `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 8G
```

## 💡 Советы и оптимизация

- **Более быстрая генерация:** Уменьшите `SD_STEPS` до `10-15`
- **Лучшее качество:** Используйте SDXL модели или увеличьте шаги до `30-40`
- **Тёмные мемы:** Попробуйте модель "Crazy Horror"
- **Аниме стиль:** Используйте модель "Anything V5"
- **Всё работает офлайн** — Не требуются API ключи!

## 🤝 Внесение вклада

Вклады приветствуются! Вот как это работает:

1. Форкните репозиторий
2. Создайте ветку для функции (`git checkout -b feature/amazing-feature`)
3. Внесите свои изменения, следуя структуре проекта
4. Добавьте тесты для новой функциональности
5. Запустите тесты: `pytest tests/`
6. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
7. Отправьте в ветку (`git push origin feature/amazing-feature`)
8. Откройте Pull Request в ветку `dev`

### Стиль кода

- Следуйте рекомендациям PEP 8
- Используйте type hints
- Добавляйте docstrings к публичным методам
- Держите классы сфокусированными и небольшими

## 📄 Лицензия

Этот проект лицензирован под MIT License — см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- [Ollama](https://ollama.com/) — Локальное LLM окружение
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) — Stable Diffusion WebUI
- [Stability AI](https://stability.ai/) — Stable Diffusion модель

## 📬 Контакты

Ссылка на проект: [https://github.com/TAskMAster339/memology-ml](https://github.com/TAskMAster339/memology-ml)

---

**Создано с ❤️ и ИИ** | Для энтузиастов мемов и практиков машинного обучения
