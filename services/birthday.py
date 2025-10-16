import json
import os
from fastapi import Depends
from datetime import date, datetime
from db.db import get_db_conn
import asyncio

# Путь к JSON-файлу лога
LOG_FILE = os.path.join(os.getcwd(), "birthday_log.json")

# Шаблоны поздравлений
MALE_TEMPLATES = [
    "С днем рождения, @{username}! 🎉 Желаю успехов и счастья!",
    "Поздравляю тебя, @{username}! Пусть день будет супер!"
]

FEMALE_TEMPLATES = [
    "С днем рождения, @{username}! 🎀 Пусть сбудутся все мечты!",
    "Поздравляю, @{username}! Пусть день будет волшебным!"
]

# --- Работа с JSON логом ---
def load_log():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_log(log_data):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=4)

def add_to_log(user_id):
    today_str = date.today().isoformat()
    log = load_log()
    log.setdefault(today_str, [])
    if user_id not in log[today_str]:
        log[today_str].append(user_id)
    save_log(log)

def has_been_congratulated(user_id):
    today_str = date.today().isoformat()
    log = load_log()
    return today_str in log and user_id in log[today_str]

# --- Авто-очистка 31 декабря ---
def clear_log_if_new_year():
    today = date.today()
    if today.month == 12 and today.day == 31:
        save_log({})

# --- Основная функция ---
async def send_birthday_congratulations(bot):
    clear_log_if_new_year()
    today_str = date.today().strftime("%m-%d")

    # Получаем курсор из пула
    async for cur in get_db_conn():  # перебор асинхронного генератора
        await cur.execute(
            "SELECT id, tg_id, username, gender FROM users_managers WHERE DATE_FORMAT(birth_date, '%%m-%%d') = %s",
            (today_str,)
        )
        users = await cur.fetchall()

        for user in users:
            user_id = user["tg_id"]
            username = user.get("username") or ""
            gender = user.get("gender") or "man"

            if has_been_congratulated(user_id):
                continue

            template = FEMALE_TEMPLATES[0] if gender.lower() == "woman" else MALE_TEMPLATES[0]
            message = template.replace("@{username}", f"@{username}" if username else "")

            try:
                await bot.send_message(user_id, message)
                add_to_log(user_id)
            except Exception as e:
                print(f"Ошибка при отправке поздравления {user_id}: {e}")