# main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

from bot.bot import bot, start_polling, set_commands  # функция запуска бота
from db.db import init_db_pool
from services.birthday import send_birthday_congratulations
from services.birthday_reminder import send_birthday_reminders
from config import FRONTEND_URLS

# --- Импорт роутеров ---
from api.employees import router as employees_router
from api.auth_routes import router as auth_router
from api.registration import router as registration
from api.roles import router as roles
from api.department import router as department
from api.chats import router as chats

# --- Инициализация FastAPI ---
app = FastAPI(title="TG Employees Backend")

# --- Настройка CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Инициализация планировщика ---
scheduler = AsyncIOScheduler()
bot_task = None  # глобальная переменная для фонового бота

now = datetime.now()
hour = now.hour
minute = (now.minute + 1) % 60 

@app.on_event("startup")
async def startup():
    """Инициализация БД, запуск бота и планировщика"""
    global bot_task
    print("🚀 Запуск приложения...")

    await init_db_pool()

    await set_commands(bot)
    print("📋 Команды бота установлены")

    # Запуск aiogram-бота в фоне
    bot_task = asyncio.create_task(start_polling())
    print("🤖 Бот запущен")

    # Настройка планировщика (ежедневно в 10:00 по серверу)
    scheduler.add_job(
        send_birthday_congratulations,
        "cron",
        hour=10, minute=30,
        args=[bot],
        id="birthday_job",
        replace_existing=True
    )

    scheduler.add_job(
        send_birthday_reminders,
        "cron",
        hour=10,
        minute=30,
        args=[bot],
        id="birthday_reminder_job",
        replace_existing=True
    )

    scheduler.start()
    print("🕓 Планировщик запущен — поздравления будут отправляться каждый день в 10:00")


@app.on_event("shutdown")
async def shutdown():
    """Остановка фоновых задач"""
    global bot_task

    print("🛑 Завершение работы...")
    scheduler.shutdown(wait=False)

    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            print("🤖 Бот остановлен")

    print("✅ Приложение корректно завершено.")


# --- Подключение роутеров ---
app.include_router(employees_router, prefix="/employees")
app.include_router(auth_router, prefix="/auth")
app.include_router(registration, prefix="/registration")
app.include_router(roles, prefix="/roles")
app.include_router(department, prefix="/department")
app.include_router(chats, prefix="/chats")


@app.get("/health")
async def health():
    """Проверка статуса API"""
    return {"status": "ok", "message": "API и бот работают"}