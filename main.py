# main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bot.bot import bot, start_polling  # функция запуска бота
from db.db import init_db_pool
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.birthday import send_birthday_congratulations

# импорт роутеров
from api.employees import router as employees_router
from api.auth_routes import router as auth_router
from api.registration import router as registration
from api.roles import router as roles
from api.department import router as department
from api.chats import router as chats

app = FastAPI(title="TG Employees Backend")

# --- CORS ---
from config import FRONTEND_URLS

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Настройка APScheduler ---
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup():
    global bot_task
    await init_db_pool()

    # Запускаем бота в фоне
    bot_task = asyncio.create_task(start_polling())

    # Запускаем APScheduler
    scheduler.start()

    # Добавляем ежедневную задачу на 9:00
    scheduler.add_job(send_birthday_congratulations, "cron", hour=13, minute=16, args=[bot])

    # Опционально: авто-очистка лога 31 декабря
    # from bot.services.birthday import clear_log_if_new_year
    # scheduler.add_job(clear_log_if_new_year, "cron", month=12, day=31, hour=23, minute=0)


@app.on_event("shutdown")
async def shutdown():
    global bot_task
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            print("Bot task cancelled")
    scheduler.shutdown()


# --- Подключение роутеров ---
app.include_router(employees_router, prefix="/employees")
app.include_router(auth_router, prefix="/auth")
app.include_router(registration, prefix="/registration")
app.include_router(roles, prefix="/roles")
app.include_router(department, prefix="/department")
app.include_router(chats, prefix="/chats")


@app.get("/health")
async def health():
    return {"status": "ok"}