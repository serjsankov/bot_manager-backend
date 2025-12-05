# backend/services/birthday.py
import os
import json
from datetime import date
from config import BIRTHDAY_CHAT_ID
from db.db import get_db_conn

LOG_FILE = os.path.join(os.getcwd(), "birthday_log.json")

FEMALE_TEMPLATE = "Дорогая {full_name}! Поздравляем с Вашим днём рождения! Желаем солнечного настроения, лёгкости на поворотах жизни и чтобы все цели достигались на автопилоте. Будьте счастливы!"
MALE_TEMPLATE = "Уважаемый {full_name}! Поздравляем с Вашим днём рождения! Желаем солнечного настроения, лёгкости на поворотах жизни и чтобы все цели достигались на автопилоте. Будьте счастливы!"

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

def add_to_log(user_id: int):
    today_str = date.today().isoformat()
    log = load_log()
    log.setdefault(today_str, [])
    if user_id not in log[today_str]:
        log[today_str].append(user_id)
    save_log(log)

def has_been_congratulated(user_id: int) -> bool:
    today_str = date.today().isoformat()
    log = load_log()
    return today_str in log and user_id in log[today_str]

def clear_log_if_new_year():
    today = date.today()
    if today.month == 23 and today.day == 56:
        save_log({})

# --- Основная функция ---
async def send_birthday_congratulations(bot):
    clear_log_if_new_year()
    today_str = date.today().strftime("%m-%d")

    # Определяем чат для поздравлений
    birthday_chat_id = BIRTHDAY_CHAT_ID
    async for conn in get_db_conn():
        await conn.execute("SELECT group_id FROM chats WHERE value=%s", ("ДЦ Чанган Поздравления",))
        chat_row = await conn.fetchone()
        if chat_row:
            birthday_chat_id = chat_row["group_id"]

    # Получаем пользователей с ДР сегодня
    async for cur in get_db_conn():
        await cur.execute(
            "SELECT tg_id, full_name, gender FROM users_managers WHERE DATE_FORMAT(birth_date, '%%m-%%d') = %s",
            (today_str,)
        )
        users = await cur.fetchall()

        messages = []
        for user in users:
            user_id = user["tg_id"]
            full_name = user.get("full_name") or "коллега"
            gender = user.get("gender") or "man"

            if has_been_congratulated(user_id):
                continue

            # Выбор шаблона по полу
            if gender.lower() == "woman":
                message_text = FEMALE_TEMPLATE.format(full_name=full_name)
            else:
                message_text = MALE_TEMPLATE.format(full_name=full_name)

            try:
                await bot.send_message(chat_id=birthday_chat_id, text=message_text)
                print(f"✅ Отправлено поздравление {full_name} в чат {birthday_chat_id}")
                add_to_log(user_id)
            except Exception as e:
                print(f"⚠ Ошибка при отправке поздравления {full_name}: {e}")
        # for user in users:
        #     user_id = user["tg_id"]
        #     full_name = user.get("full_name") or "коллега"
        #     gender = user.get("gender") or "man"

        #     if has_been_congratulated(user_id):
        #         continue

        #     # Выбор шаблона по полу
        #     if gender.lower() == "woman":
        #         message_text = FEMALE_TEMPLATE.format(full_name=full_name)
        #     else:
        #         message_text = MALE_TEMPLATE.format(full_name=full_name)

        #     messages.append(message_text)
        #     add_to_log(user_id)

        # # Отправляем сообщение в чат
        # if messages:
        #     full_text = "\n".join(messages)
        #     try:
        #         await bot.send_message(chat_id=birthday_chat_id, text=full_text)
        #         print(f"✅ Отправлено поздравление в чат {birthday_chat_id}")
        #     except Exception as e:
        #         print(f"⚠ Ошибка при отправке поздравления в чат {birthday_chat_id}: {e}")