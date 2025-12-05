# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

FRONTEND_URLS = [
    "https://itmastery.ru",     # продакшн
    "http://localhost:5173",    # локальный фронт
    "http://127.0.0.1:5173"     # на случай другого хоста
]

BIRTHDAY_CHAT_ID="-1002993387577"
