# 🧠 Memology-ML — Движок генерации мемов с ИИ для сервиса **Memology**

[Link to English README.md](README.md)

**Memology-ML** — это основной ML компонент проекта **Memology** —  
платформы для генерации мемов с помощью искусственного интеллекта.  
Этот модуль отвечает за создание **визуального контента мемов** и **смешных подписей** с использованием [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) и [Ollama (LLaMA 3.2)](https://ollama.com/library/llama3.2).
Вся обработка выполняется **локально**, поэтому ваши мемы создаются **приватно и офлайн**.

## 🎨 Примеры мемов

| Входная идея              | Сгенерированный мем                               |
| ------------------------- | ------------------------------------------------- |
| «кот пьет кофе»           | ![cat meme](examples/cat_with_coffee_example.png) |
| «лошадь чихнула»          | ![night coder meme](examples/horse_example.png)   |
| «компьютер и ежу понятен» | ![computer meme](examples/computer_example.png)   |

---

## 🚀 Возможности

- 🖼️ Генерация мемов высокого качества локально
- 🎨 Случайные визуальные стили (реалистичный, аниме, хоррор и др.)
- 🧠 Генерация английских промптов по русским идеям
- 😂 Короткие забавные подписи на русском языке
- ✍️ Автоматическое наложение текста шрифтом Impact
- 📜 Полное логирование процесса генерации
- 💾 Сохранение изображений в папке `generated_images/`

---

## ⚙️ Установка

### 1️⃣ Клонируйте репозиторий

```bash
git clone https://github.com/TAskMAster339/memology-ml.git
cd meme-generator
```

### 2️⃣ Создайте и активируйте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate    # Linux / macOS
```

### 3️⃣ Установите зависимости

```bash
pip install -r requirements.txt
```

## 🧠 Конфигурация Ollama

Ollama используется для генерации текстовых промптов и подписей.

### Установка Ollama

👉 [https://ollama.com/download](https://ollama.com/download)

### Загрузите модель LLaMA 3.2

```bash
ollama pull llama3.2:2b
```

Проверьте, что она работает:

```bash
ollama run llama3.2:2b
```

---

## 🎨 Конфигурация Stable Diffusion WebUI

Stable Diffusion WebUI (от AUTOMATIC1111) используется для генерации изображений.

### 1️⃣ Установите WebUI

👉 [https://github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 2️⃣ Запустите WebUI с включённым API

```bash
python launch.py --api
```

API будет доступен по адресу:

```bash
http://127.0.0.1:7860/sdapi/v1/txt2img
```

### 3️⃣ (Необязательно) Добавьте пользовательские модели

Вы можете скачать дополнительные модели с [Civitai](https://civitai.com):

| Модель           | Стиль                              | Ссылка                                                                                             |
| ---------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Memes XL**     | Мемный-стиль, смешно, резонирующий | [https://civitai.com/models/205229/memes-xl](https://civitai.com/models/205229/memes-xl)           |
| **Crazy Horror** | Темный, сюрреалистичный, ужасающий | [https://civitai.com/models/1101129/crazy-horror](https://civitai.com/models/1101129/crazy-horror) |

Сохраните загруженные файлы `.safetensors` в папку:

```
stable-diffusion-webui/models/Stable-diffusion/
```

---

## 🧩 Конфигурация

- **Модель LLM:** `llama3.2:2b`
- **Семплер:** `Euler a`
- **Кол-во шагов:** 20
- **Температура:** 7
- **Разрешение:** 512×512

Вы можете изменить эти параметры в функции `generate_image()` в файле `main.py`.

---

## 🧠 Использование

Просто выполните:

```bash
python main.py
```

1. Программа выполнит следующие шаги:
2. Возьмёт короткую идею (например, «кот пьет кофе»)
3. Сгенерирует подробное описание сцены на английском
4. Создаст короткую, смешную подпись на русском
5. Сгенерирует изображение в случайном стиле (аниме, реализм, хоррор и др.)
6. Наложит подпись в формате мема
7. Сохранит и залогирует результат

---

## 📜 Логирование

Каждая генерация сохраняется в `generation.log`, например:

```
2025-10-14 23:40:54 | INFO | Model: llama3.2:3b | Prompt: кот пьет кофе | Visual: A small white kitten sits at a tiny wooden table, its fur fluffed up slightly as it gazes intently at a delicate china cup filled with steaming hot coffee... | Caption: Кот пьет кофе, а я пью чай. | RawFile: meme_20251014_234051_15f351c6_raw.png | FinalFile: meme_20251014_234054_b3e571e5_final.png | Time: 169.58s
```

---

## 📁 Структура проекта

```
meme-generator/
│
├── examples/              # примеры мемов (для README)
├── generated_images/      # автогенерируемые мемы
├── impact.ttf             # шрифт для мемов
├── main.py                # основная программа
├── requirements.txt       # зависимости
├── generation.log         # лог-файл
└── README.md              # этот файл
```

## 🖼 Папка `examples/`

Добавьте сюда несколько примеров мемов для README:

```
examples/cat_with_coffee_example.png
examples/horse_example.png
examples/computer_example.png
```

Они будут отображаться в верхней части README.

---

## ⭐️ Участие в разработке

Будем рады вашим улучшениям!
Вы можете улучшить генерацию подписей, добавить новые стили изображений или оптимизировать производительность.

---

## 🧰 Советы

- Уменьшите параметр steps до 15 для более быстрой генерации.
- Используйте SDXL или Anything V5 для более реалистичных изображений.
- Попробуйте Crazy Horror для тёмных сюрреалистичных мемов.
- Всё работает офлайн — никакие API-ключи не требуются!
