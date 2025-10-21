from fastapi import APIRouter, Depends, HTTPException, Header, Request
from db.db import get_db_conn
from .auth import telegram_user
from services.telegram import add_user_to_chat, notify_user_about_group, notify_user_about_removal, notify_user_approved, check_bot_in_chat, remove_user_from_chat, notify_manager_fired
router = APIRouter()

# Простая проверка пользователя: Telegram или Demo
# async def telegram_user(
#     x_telegram_init_data: str = Header(None),
#     x_demo_user: str = Header(None),
# ):
#     if x_demo_user:
#         return {
#             "id": 12345,
#             "username": "demo_user",
#             "role": "director",  # роль для интерфейса
#             "is_demo": True
#         }
#     if not x_telegram_init_data:
#         raise HTTPException(status_code=401, detail="Unauthorized")
    
#     # Разбор init_data Telegram
#     user_id = parse_init_data(x_telegram_init_data)["id"]
#     return {"id": user_id, "role": "manager"}  # пока заглушка

@router.get("/")
async def list_employees(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM users_managers")  # ⚡ execute
    rows = await db.fetchall()                   # ⚡ fetchall
    return rows                                  # DictCursor уже возвращает словари

# @router.get("/department")
# async def list_employees_department(user=Depends(telegram_user), db=Depends(get_db_conn)):
#     await db.execute("SELECT * FROM users_managers WHERE manager=%s", (user['full_name'],))
#     users = await db.fetchall()
#     return users

@router.get("/department")
async def list_employees_department(
    user=Depends(telegram_user),
    db=Depends(get_db_conn)
):
    # Ищем пользователя
    await db.execute(
        "SELECT * FROM users_managers WHERE username = %s",
        (user["username"],)
    )
    users = await db.fetchall()

    if not users:
        # raise HTTPException(status_code=404, detail="User not found")
        return []

    current_user = users[0]  # Берём первую запись

    if current_user["role"] == "директор":
        await db.execute(
            "SELECT * FROM users_managers WHERE role NOT IN (%s)",
            ("директор",)
        )
        return await db.fetchall()

    elif current_user["role"] == "Руководитель":
        await db.execute(
            "SELECT * FROM users_managers WHERE phone_manager = %s",
            (current_user["phone"],)
        )
        return await db.fetchall()

    else:
        raise HTTPException(status_code=403, detail="Access denied")

@router.get("/managers")
async def list_employees_manager(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM users_managers WHERE role=%s", ('руководитель',))
    users = await db.fetchall()
    return users

@router.get("/all")
async def list_employees_all(user=Depends(telegram_user), db=Depends(get_db_conn)):
    # await db.execute("SELECT * FROM users_managers WHERE role NOT IN (%s, %s)", ('руководитель', 'директор'))
    query = """
        SELECT 
            um.*, 
            d.id AS department_id
        FROM users_managers um
        LEFT JOIN department d 
            ON um.department = d.value
    """
    await db.execute(query)
    users = await db.fetchall()
    return users

@router.post("/")
async def detail_employee(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()

    # await db.execute("SELECT full_name, phone, role, phone_manager FROM users_managers WHERE id=%s", (data['id']))
    # data_user = await db.fetchall()
    # return data_user
    await db.execute("""
    SELECT u.id, u.full_name, u.phone, u.role, u.phone_manager, u.birth_date, u.status, uc.chat_id
    FROM users_managers u
    LEFT JOIN user_chats uc ON u.id = uc.user_id
    WHERE u.id = %s
    """, (data['id'],))

    rows = await db.fetchall()

    user = {
        "id": rows[0]["id"],
        "full_name": rows[0]["full_name"],
        "phone": rows[0]["phone"],
        "role": rows[0]["role"],
        "birth_date": rows[0]["birth_date"],
        # "phone_manager": rows[0]["phone_manager"],
        "status": rows[0]["status"],
        "chats": [r["chat_id"] for r in rows if r["chat_id"] is not None]
    }
    return user

@router.post("/user/")
async def edit_user_data(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    emp_id = data.pop("id", None)
    if not emp_id:
        return {"error": "id is required"}

    # --- 1. Получаем пользователя ---
    await db.execute("SELECT * FROM users_managers WHERE id=%s", (emp_id,))
    user_data = await db.fetchone()
    if not user_data:
        return {"error": "user not found"}

    old_phone = user_data["phone"]
    new_phone = data.get("phone")
    role = user_data["role"].lower()

    # --- 2. Проверяем, изменился ли телефон ---
    relation_field = None
    if role == "директор":
        relation_field = "phone_director"
    elif role == "руководитель":
        relation_field = "phone_manager"

    if new_phone and new_phone != old_phone:
        # Обновляем телефон у подчинённых, если нужно
        if relation_field:
            query = f"""
                UPDATE users_managers
                SET {relation_field}=%s
                WHERE {relation_field}=%s
            """
            await db.execute(query, (new_phone, old_phone))

    # --- 3. Обновляем все остальные поля пользователя ---
    fields = []
    values = []
    for key, value in data.items():
        if key != "id":
            fields.append(f"{key} = %s")
            values.append(value)

    if fields:
        query = f"UPDATE users_managers SET {', '.join(fields)} WHERE id = %s"
        values.append(emp_id)
        await db.execute(query, values)

    # --- 4. Возвращаем обновлённые данные пользователя ---
    await db.execute("SELECT * FROM users_managers WHERE id=%s", (emp_id,))
    return await db.fetchone()

@router.post("/edit/")
async def change_employee(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    emp_id = data.pop("id", None)
    if not emp_id:
        return {"error": "id is required"}

    # --- Проверяем статус из тела запроса ---
    status = data.get("status")

    # Если в запросе пришёл pending — автоматически меняем на approved
    if status == "pending":
        data["status"] = "approved"  # <--- меняем прямо в запросе

        # Уведомляем пользователя
        await db.execute("SELECT tg_id FROM users_managers WHERE id=%s", (emp_id,))
        res = await db.fetchone()
        tg_id = res.get("tg_id") if res else None

        if tg_id:
            await notify_user_approved(tg_id)

    # --- 1. Обновляем поля пользователя ---
    fields = []
    values = []
    for key, value in data.items():
        if key != "chat_ids":  # chat_ids обработаем отдельно
            fields.append(f"{key} = %s")
            values.append(value)

    if fields:
        query = f"UPDATE users_managers SET {', '.join(fields)} WHERE id = %s"
        values.append(emp_id)
        await db.execute(query, values)

    # --- 2. Обновляем чаты пользователя ---
    new_chat_ids = set(data.get("chat_ids", []))
    await db.execute("SELECT chat_id FROM user_chats WHERE user_id=%s", (emp_id,))
    old_chat_ids = {row["chat_id"] for row in await db.fetchall()}

    to_add = new_chat_ids - old_chat_ids
    to_remove = old_chat_ids - new_chat_ids

    # Добавляем новые чаты
    if to_add:
        # Добавляем в БД
        await db.executemany(
            "INSERT IGNORE INTO user_chats (chat_id, user_id) VALUES (%s, %s)",
            [(cid, emp_id) for cid in to_add]
        )
        # Получаем ссылки и group_id чатов
        await db.execute(
            "SELECT group_id, link, value FROM chats WHERE id IN %s",
            (tuple(to_add),)
        )
        new_chats = await db.fetchall()

        for chat in new_chats:
            group_id = chat["group_id"]
            link = chat["link"]
            name = chat["value"]
            tg_id = None
            # Получаем Telegram ID пользователя
            await db.execute("SELECT tg_id FROM users_managers WHERE id=%s", (emp_id,))
            res = await db.fetchone()
            tg_id = res.get("tg_id") if res else None

            if tg_id:
                try:
                    # Отправляем ссылку пользователю
                    text = f"✅ Вы добавлены в группу: {name}\nСсылка: {link}" if link else f"✅ Вы добавлены в группу: {name}"
                    await notify_user_about_group(tg_id, text)
                except Exception as e:
                    print(f"⚠ Не удалось уведомить {tg_id} о чате {name}: {e}")
            # Бота проверяем и добавляем, если нужно
            try:
                bot_in_chat = await check_bot_in_chat(group_id)
                if not bot_in_chat:
                    print(f"⚠ Бот не имеет доступа к чату {group_id}")
            except Exception as e:
                print(f"⚠ Ошибка проверки бота в чате {group_id}: {e}")

    # Удаляем старые чаты
    if to_remove:
        await db.execute(
            "DELETE FROM user_chats WHERE user_id=%s AND chat_id IN %s",
            (emp_id, tuple(to_remove))
        )
        # Можно добавить уведомление об удалении, если нужно
        await db.execute(
            "SELECT group_id, value FROM chats WHERE id IN %s",
            (tuple(to_remove),)
        )
        removed_chats = await db.fetchall()
        await db.execute("SELECT tg_id FROM users_managers WHERE id=%s", (emp_id,))
        res = await db.fetchone()
        tg_id = res.get("tg_id") if res else None
        if tg_id:
            for chat in removed_chats:
                try:
                    await notify_user_about_removal(tg_id, chat["value"])
                except Exception as e:
                    print(f"⚠ Не удалось уведомить {tg_id} об удалении из {chat['value']}: {e}")

    # --- 3. Возвращаем обновлённого пользователя и сотрудников ---
    await db.execute(
        "SELECT id, full_name, phone, role, phone_manager, status, birth_date FROM users_managers WHERE id=%s",
        (emp_id,)
    )
    updated_row = await db.fetchone()

    await db.execute("SELECT * FROM users_managers")
    users = await db.fetchall()
    # --- Получаем текущие чаты пользователя после обновлений ---
    await db.execute("""
        SELECT uc.chat_id, c.value AS chat_name
        FROM user_chats uc
        JOIN chats c ON uc.chat_id = c.id
        WHERE uc.user_id = %s
    """, (emp_id,))
    chat_rows = await db.fetchall()

    # Список ID чатов
    user_chat_ids = [row["chat_id"] for row in chat_rows]

    # Словарь или список с названиями чатов
    user_chats = [{"id": row["chat_id"], "name": row["chat_name"]} for row in chat_rows]

    return {
        "updated_row": updated_row,
        "users": users,
        "chat_ids": user_chat_ids,
        "chats": user_chats
    }

@router.post('/delete/')
async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    emp_id = data.get("id")

    if not emp_id:
        return {"error": "id is required"}

    # 1. Получаем пользователя
    await db.execute("SELECT * FROM users_managers WHERE id=%s", (emp_id,))
    user_row = await db.fetchone()
    if not user_row:
        return {"error": f"User with id {emp_id} not found"}

    tg_id = user_row.get("tg_id")
    full_name = user_row.get("full_name")
    role = user_row.get("role")
    department = user_row.get("department")

    if not tg_id:
        print("⚠ Пользователь не привязан к Telegram, пропуск удаления из TG")
        tg_id = None

    # 2. Берём все реальные group_id из таблицы chats через JOIN
    await db.execute("""
        SELECT c.group_id, c.value
        FROM user_chats uc
        JOIN chats c ON uc.chat_id = c.id
        WHERE uc.user_id = %s
    """, (emp_id,))
    chat_rows = await db.fetchall()

    # 3. Удаляем из Telegram чатов
    if tg_id:
        for chat in chat_rows:
            group_id = chat["group_id"]
            group_name = chat["value"]

            if not group_id:
                print(f"⚠ У чата {group_name} нет group_id — пропускаем")
                continue

            try:
                await remove_user_from_chat(int(group_id), int(tg_id))
                await notify_user_about_removal(tg_id, group_name)
                await notify_manager_fired(
                    user["tg_id"],
                    full_name,   # имя уволенного сотрудника
                    role,
                    department
                )
                print(f"✅ Удалён {tg_id} из TG-чата {group_name} ({group_id})")
            except Exception as e:
                print(f"❌ Ошибка удаления {tg_id} из чата {group_id}: {e}")

        # --- Получаем всех директоров и уведомляем ---
    await db.execute("SELECT tg_id, full_name, department, role FROM users_managers WHERE role='директор' AND tg_id IS NOT NULL")
    directors = await db.fetchall()
    for director in directors:
        try:
            await notify_manager_fired(
                director["tg_id"],
                full_name,   # имя уволенного сотрудника
                role,
                department
            )
            print(f"Директор {director['full_name']} уведомлен об увольнении {full_name}")
        except Exception as e:
            print(f"Не удалось уведомить директора {director['full_name']}: {e}")

    # 4. Удаляем связи в БД
    await db.execute("DELETE FROM user_chats WHERE user_id=%s", (emp_id,))
    await db.execute("DELETE FROM users_managers WHERE id=%s", (emp_id,))

    # await db.commit()

    # 5. Возвращаем обновлённый список
    await db.execute("SELECT * FROM users_managers")
    return await db.fetchall()
