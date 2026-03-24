import os
import sys
from pathlib import Path

# Принудительно указываем путь к .env файлу
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"Загружено: {key}=***")  # Для отладки

# Теперь читаем переменные
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8679539873:AAFsD-Gc3-rU2zzyOy2yJjxrbI5hEILXtNg")
PROJECT_PATH = os.getenv("PROJECT_PATH", "/home/u123456/project")
ALLOWED_USERS = [int(id.strip()) for id in os.getenv("ALLOWED_USERS", "8346538289").split(",")]
AI_PROVIDER = "builtin"

# Проверка для отладки
print(f"TELEGRAM_TOKEN загружен: {'Да' if TELEGRAM_TOKEN else 'Нет'}")
print(f"Длина токена: {len(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else 0}")
