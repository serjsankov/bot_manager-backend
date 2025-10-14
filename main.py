# main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bot.bot import start_polling  # импорт функции
from db.db import init_db_pool

# импорт роутера
from api.employees import router as employees_router
from api.auth_routes import router as auth_router
from api.registration import router as registration
from api.roles import router as roles
from api.department import router as department
from api.chats import router as chats

app = FastAPI(title="TG Employees Backend")

# CORS
from config import FRONTEND_URLS
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    global bot_task
    await init_db_pool()
    # Запускаем бота в фоне и сохраняем задачу
    bot_task = asyncio.create_task(start_polling())

@app.on_event("shutdown")
async def shutdown():
    global bot_task
    if bot_task:
        bot_task.cancel()  # корректно отменяем задачу
        try:
            await bot_task
        except asyncio.CancelledError:
            print("Bot task cancelled")

# app.include_router(...)
# подключаем роутер к пути /employees
app.include_router(employees_router, prefix="/employees")
app.include_router(auth_router, prefix="/auth")
app.include_router(registration, prefix="/registration")
app.include_router(roles, prefix="/roles")
app.include_router(department, prefix="/department")
app.include_router(chats, prefix="/chats")

@app.get("/health")
async def health():
    return {"status": "ok"}