import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")

# Путь к проекту
PROJECT_PATH = os.getenv("PROJECT_PATH", "/home/user/my_project")

# Разрешённые пользователи
ALLOWED_USERS = [int(id) for id in os.getenv("ALLOWED_USERS", "123456789").split(",")]

# AI провайдер - теперь только builtin (встроенный)
AI_PROVIDER = "builtin"  # встроенный AI, не требует API