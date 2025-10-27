FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p logs generated_images

# Порт для FastAPI
EXPOSE 8000

# По умолчанию запускаем FastAPI (переопределяется в docker-compose)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
