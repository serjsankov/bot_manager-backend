from datetime import date, timedelta
from db.db import get_db_conn

async def send_birthday_reminders(bot):
    tomorrow_str = (date.today() + timedelta(days=1)).strftime("%m-%d")
    print("🎂 send_birthday_reminders запущен!")

    async for conn in get_db_conn():
        # Получаем пользователей, у которых завтра день рождения
        await conn.execute(
            "SELECT id, full_name, role, phone_manager, phone FROM users_managers WHERE DATE_FORMAT(birth_date, '%%m-%%d') = %s",
            (tomorrow_str,)
        )
        birthday_users = await conn.fetchall()

        if not birthday_users:
            print("ℹ️ Завтра ни у кого нет дня рождения.")
            return

        # Получаем директора и всех руководителей
        await conn.execute("SELECT tg_id, full_name, phone FROM users_managers WHERE role = 'директор'")
        director = await conn.fetchone()

        await conn.execute("SELECT tg_id, full_name, phone FROM users_managers WHERE role = 'руководитель'")
        all_managers = await conn.fetchall()

        for user in birthday_users:
            user_name = user["full_name"]
            user_role = (user["role"] or "").lower()
            user_manager_phone = user.get("phone_manager")
            user_phone = user.get("phone")

            message_text = f"📣 Завтра день рождения у: {user_name}"

            recipients = []

            # --- 🎂 Если день рождения у руководителя ---
            if user_role == "руководитель":
                recipients = [m for m in all_managers if m["phone"] != user_phone]  # другие руководители
                if director:
                    recipients.append(director)

            # --- 🎂 Если день рождения у обычного сотрудника ---
            elif user_role not in ("директор", "руководитель"):
                if director:
                    recipients.append(director)
                if user_manager_phone:
                    manager = next((m for m in all_managers if m["phone"] == user_manager_phone), None)
                    if manager:
                        recipients.append(manager)

            # --- 🎂 Если день рождения у директора ---
            elif user_role == "директор":
                recipients = all_managers  # уведомляем всех руководителей

            # --- Отправляем уведомления ---
            for r in recipients:
                if not r.get("tg_id"):
                    continue

                try:
                    await bot.send_message(
                        chat_id=r["tg_id"],
                        text=f"Здравствуйте, {r['full_name']}!\n{message_text}"
                    )
                    print(f"✅ Уведомление отправлено {r['full_name']}")
                except Exception as e:
                    print(f"⚠ Ошибка при отправке уведомления {r['full_name']}: {e}")