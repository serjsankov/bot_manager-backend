from fastapi import APIRouter, Depends, Request, HTTPException
from db.db import get_db_conn
from .auth import telegram_user
from services.telegram import check_bot_in_chat, update_chat_title, notify_user_about_group, notify_user_about_removal, remove_user_from_chat

router = APIRouter()

@router.get("/")
async def list_chats(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM chats")  # ⚡ execute
    rows = await db.fetchall()                   # ⚡ fetchall
    return rows                                  # DictCursor уже возвращает словари

@router.post("/")
async def add_chat(data: dict, request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
     # 1. Создаем новый чат
    value = data.get("value")
    link = data.get("link")
    group_id = data.get("group_id")

    # 1️⃣ Проверяем, добавлен ли бот в чат
    is_accessible = await check_bot_in_chat(group_id)
    if not is_accessible:
        raise HTTPException(status_code=400, detail="Бот не добавлен в этот чат или ссылка недействительна")
    
    # 2️⃣ Проверяем, есть ли чат в БД
    await db.execute("SELECT id FROM chats WHERE group_id = %s", (group_id,))
    existing = await db.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Этот чат уже существует")
    
    # 3️⃣ Добавляем чат
    await db.execute(
        "INSERT INTO chats (value, group_id, link) VALUES (%s, %s, %s)",
        (value, group_id, link)
    )

    await db.execute("SELECT LAST_INSERT_ID() AS id")
    row = await db.fetchone()
    new_chat_id = row["id"]


    users_ids = data.get("users_ids", [])
    if users_ids:
        values = [(user_id, new_chat_id) for user_id in users_ids]
        await db.executemany(
            "INSERT IGNORE INTO user_chats (user_id, chat_id) VALUES (%s, %s)",
            values
        )

        # 5️⃣ Отправляем уведомление каждому пользователю
        # for user_id in users_ids:
        #     text = (
        #         f"Здравствуй!\n"
        #         f"Вы были добавлены в новый чат.\n"
        #         f"Название чата: {value}\n"
        #         f"Chat ID: {group_id}\n"
        #         f"Теперь вы можете отслеживать сообщения этого чата."
        #     )
        #     try:
        #         await send_message_safe(user_id, text)
        #     except Exception as e:
        #         print(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")

    await db.execute("SELECT * FROM chats")
    rows = await db.fetchall()
    return rows


@router.post("/delete")
async def delete_chat(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    chat_id = data.pop("id", None)

    if not chat_id:
        return {"error": "id is required"}

    await db.execute("DELETE FROM chats WHERE id=%s", (chat_id,))

    await db.execute("DELETE FROM user_chats WHERE chat_id=%s", (chat_id))
    await db.execute("DELETE FROM role_chat WHERE chat_id=%s", (chat_id))

    await db.execute("SELECT * FROM chats")
    chats = await db.fetchall()
    return chats

@router.post("/data")
async def all_data_role( request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    chat_id = data.get("id")

    # получаем чат
    await db.execute("SELECT * FROM chats WHERE id=%s", (chat_id,))
    chat = await db.fetchone()

    # получаем сотрудников, связанных с этим чатом
    await db.execute("""
        SELECT 
            um.id,
            um.full_name,
            um.department,
            um.role,
            um.username
        FROM user_chats uc
        JOIN users_managers um ON uc.user_id = um.id
        WHERE uc.chat_id = %s
    """, (chat_id,))
    employees = await db.fetchall()

    return {
        "chat": chat,
        "employees": employees,
    }

@router.post("/edit/")
async def change_role(request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    chat_id = data.get("id")  # внутренний id таблицы chats
    new_value = data.get("value")  # новое имя группы
    new_user_ids = set(data.get("user_ids", []))

    # --- 1. Получаем старые данные
    await db.execute("SELECT value, group_id, link FROM chats WHERE id=%s", (chat_id,))
    row = await db.fetchone()
    if not row:
        return {"error": "Чат не найден"}

    old_value = row["value"]
    group_id = row["group_id"]  # настоящий Telegram chat_id
    group_link = row["link"]

    # --- 2. Получаем старых участников
    await db.execute("SELECT user_id FROM user_chats WHERE chat_id=%s", (chat_id,))
    old_user_ids = {u["user_id"] for u in await db.fetchall()}

    to_add = new_user_ids - old_user_ids
    to_remove = old_user_ids - new_user_ids

    # --- 3. Обновляем название группы в БД
    await db.execute("UPDATE chats SET value=%s WHERE id=%s", (new_value, chat_id))

    # --- 4. Обновляем связи пользователей в БД
    if to_add:
        await db.executemany(
            "INSERT IGNORE INTO user_chats (chat_id, user_id) VALUES (%s, %s)",
            [(chat_id, uid) for uid in to_add]
        )
    if to_remove:
        await db.execute(
            "DELETE FROM user_chats WHERE chat_id=%s AND user_id IN %s",
            (chat_id, tuple(to_remove))
        )

    # --- 5. Меняем название телеграм-группы
    if new_value != old_value:
        print(f"🛠 Меняю название Telegram группы {group_id}: '{old_value}' → '{new_value}'")
        await update_chat_title(group_id, new_value)

    # --- 6. Получаем ссылку на группу
    # try:
    #     chat = await bot.get_chat(group_id)
    #     invite_link = getattr(chat, "invite_link", None)
    #     if not invite_link:
    #         print(f"⚠ Нет ссылки на группу {group_id}")
    # except Exception as e:
    #     invite_link = None
    #     print(f"⚠ Не удалось получить ссылку на группу: {e}")

    # --- 7. Оповещаем новых пользователей и добавляем в группу
    if to_add:
        await db.execute("SELECT tg_id FROM users_managers WHERE id IN %s", (tuple(to_add),))
        tg_users = await db.fetchall()

        for u in tg_users:
            tg_id = u["tg_id"]
            if tg_id:
                # Отправляем ссылку на группу
                text = f"{new_value}"
                if group_link:
                    text += f"\nСсылка на группу: {group_link}"
                try:
                    await notify_user_about_group(tg_id, text)
                except Exception as e:
                    print(f"⚠ Не удалось отправить уведомление пользователю {tg_id}: {e}")
            else:
                print(f"⚠ У пользователя нет telegram_id, пропускаю: {u}")

    # --- 8. Оповещаем и исключаем удалённых пользователей
    if to_remove:
        await db.execute("SELECT tg_id FROM users_managers WHERE id IN %s", (tuple(to_remove),))
        tg_users_removed = await db.fetchall()

        for u in tg_users_removed:
            tg_id = u["tg_id"]
            if tg_id:
                try:
                    # 🧹 Удаляем пользователя из Telegram-группы
                    await remove_user_from_chat(group_id, tg_id)

                    # 📨 Отправляем уведомление об удалении
                    await notify_user_about_removal(tg_id, new_value)

                except Exception as e:
                    print(f"⚠ Не удалось удалить {tg_id} из Telegram-группы {group_id}: {e}")
            else:
                print(f"⚠ У удалённого пользователя нет telegram_id, пропускаю: {u}")

    # --- 9. Финальный ответ
    await db.execute("SELECT * FROM chats")
    chats = await db.fetchall()

    return {"success": True, "updated_chat": chat_id, "chats": chats}
