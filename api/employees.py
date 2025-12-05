from fastapi import APIRouter, Depends, HTTPException, Header, Request
from db.db import get_db_conn
from .auth import telegram_user
from services.telegram import send_message_editing, notify_user_about_group, notify_user_about_removal, notify_user_approved, check_bot_in_chat, remove_user_from_chat, notify_manager_fired
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

    await db.execute("SELECT is_manager FROM roles WHERE value=%s", (current_user["role"],))
    role_manager = await db.fetchone()
    is_manager = bool(role_manager['is_manager']) if role_manager else False

    if current_user["role"] == "директор" or current_user["role"] == "admin":
        await db.execute(
            "SELECT * FROM users_managers WHERE LOWER(role) NOT IN (%s)",
            ("директор",)
        )
        return await db.fetchall()

    elif is_manager:
        await db.execute("""
            SELECT u.*
            FROM users_managers u
            JOIN roles r ON u.role = r.value
            WHERE u.phone_manager = %s
            AND r.is_manager = 0
        """, (current_user["phone"],))
        return await db.fetchall()

    else:
        raise HTTPException(status_code=403, detail="Access denied")

# @router.get("/managers")
# async def list_employees_manager(user=Depends(telegram_user), db=Depends(get_db_conn)):
#     await db.execute("SELECT * FROM users_managers WHERE LOWER(role)=%s", ('руководитель',))
#     users = await db.fetchall()
#     return users
@router.get("/managers")
async def list_employees_manager(user=Depends(telegram_user), db=Depends(get_db_conn)):
    # Получаем пользователей, у которых роль помечена как руководящая
    await db.execute("""
        SELECT um.* 
        FROM users_managers um
        JOIN roles r ON um.role = r.value
        WHERE r.is_manager = 1
    """)
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
    SELECT u.id, u.full_name, u.phone, u.role, u.phone_manager, u.birth_date, u.status, u.manager, u.director, u.phone_director, uc.chat_id
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
        "phone_manager": rows[0]["phone_manager"],
        "status": rows[0]["status"],
        "manager": rows[0]["manager"],
        "director": rows[0]["director"],
        "phone_director": rows[0]["phone_director"],
        "chats": [r["chat_id"] for r in rows if r["chat_id"] is not None]
    }
    return user

# @router.post("/user/")
# async def edit_user_data(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
#     data = await request.json()
#     emp_id = data.pop("id", None)
#     if not emp_id:
#         return {"error": "id is required"}

#     # --- 1. Получаем пользователя ---
#     await db.execute("SELECT * FROM users_managers WHERE id=%s", (emp_id,))
#     user_data = await db.fetchone()
#     if not user_data:
#         return {"error": "user not found"}

#     old_phone = user_data["phone"]
#     new_phone = data.get("phone")
#     role = user_data["role"].lower()

#     # --- 2. Проверяем, изменился ли телефон ---
#     relation_field = None
#     if role == "директор":
#         relation_field = "phone_director"
#     elif role == "руководитель":
#         relation_field = "phone_manager"

#     if new_phone and new_phone != old_phone:
#         # Обновляем телефон у подчинённых, если нужно
#         if relation_field:
#             query = f"""
#                 UPDATE users_managers
#                 SET {relation_field}=%s
#                 WHERE {relation_field}=%s
#             """
#             await db.execute(query, (new_phone, old_phone))

#     # --- 3. Обновляем все остальные поля пользователя ---
#     fields = []
#     values = []
#     for key, value in data.items():
#         if key != "id":
#             fields.append(f"{key} = %s")
#             values.append(value)

#     if fields:
#         query = f"UPDATE users_managers SET {', '.join(fields)} WHERE id = %s"
#         values.append(emp_id)
#         await db.execute(query, values)

#     # --- 4. Возвращаем обновлённые данные пользователя ---
#     await db.execute("SELECT * FROM users_managers WHERE id=%s", (emp_id,))
#     return await db.fetchone()
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

    old_name = user_data["full_name"]
    new_name = data.get("full_name")

    role = user_data["role"].lower()

    await db.execute("SELECT is_manager FROM roles WHERE value=%s", (role,))
    role_manager = await db.fetchone()
    is_manager = bool(role_manager['is_manager']) if role_manager else False

    # --- 2. Проверяем роль пользователя ---
    if role == "директор":
        # Обновляем имя директора и телефон только у руководителей
        if new_name and new_name != old_name:
            await db.execute(
                "UPDATE users_managers u JOIN roles r ON LOWER(u.role) = LOWER(r.value) SET u.director=%s WHERE u.director=%s AND r.is_manager = 1",
                (new_name, old_name),
            )

        if new_phone and new_phone != old_phone:
            await db.execute(
                """
                UPDATE users_managers u
                JOIN roles r ON u.role = r.value
                SET u.phone_director = %s
                WHERE u.phone_director = %s
                AND r.is_manager = 1
                """,
                (new_phone, old_phone),
            )

    elif is_manager:
        # Обновляем имя руководителя и телефон у сотрудников
        if new_name and new_name != old_name:
            await db.execute(
                "UPDATE users_managers SET manager=%s WHERE manager=%s",
                (new_name, old_name),
            )

        if new_phone and new_phone != old_phone:
            await db.execute(
                "UPDATE users_managers SET phone_manager=%s WHERE phone_manager=%s",
                (new_phone, old_phone),
            )

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

    # --- ДО ОБНОВЛЕНИЯ проверяем, новая ли роль руководителя ---
    new_role = data.get("role")
    if new_role:
        await db.execute("SELECT is_manager FROM roles WHERE value=%s", (new_role.lower(),))
        role_row = await db.fetchone()
        is_manager = bool(role_row['is_manager']) if role_row else False

        if is_manager:
            # Получаем директора для нового руководителя
            await db.execute("SELECT full_name, phone FROM users_managers WHERE LOWER(role)='директор' AND status='approved' LIMIT 1")
            director_row = await db.fetchone()
            if director_row:
                fields.append("director = %s")
                values.append(director_row["full_name"])
                fields.append("phone_director = %s")
                values.append(director_row["phone"])

            # Для руководителя его "менеджер" — это он сам
            fields.append("manager = %s")
            values.append(data.get("full_name"))  # или updated full_name
            fields.append("phone_manager = %s")
            values.append(data.get("phone"))      # или updated phone

            # Добавляем должность в сводную таблицу users_dep
            # Проверяем существующую связь
            await db.execute("""
                SELECT 1
                FROM users_dep ud
                JOIN department d ON ud.dep_id = d.id
                WHERE ud.user_id=%s AND d.value=%s
            """, (emp_id, new_role))
            exists = await db.fetchone()
            if not exists:
                # Получаем id отдела по значению роли
                await db.execute("SELECT id FROM department WHERE value=%s", (new_role,))
                dep_row = await db.fetchone()
                if dep_row:
                    await db.execute(
                        "INSERT INTO users_dep (user_id, dep_id) VALUES (%s, %s)",
                        (emp_id, dep_row["id"])
                    )

            # Ставим NULL в колонку department основной таблицы
            fields.append("department = NULL")

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
                    await remove_user_from_chat(chat["group_id"], tg_id)
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

    # --- 4.1. Уведомления о редактировании пользователя ---
    await db.execute(
        "SELECT tg_id, role, phone_manager, full_name, phone, birth_date, department FROM users_managers WHERE id=%s",
        (emp_id,)
    )
    user_row = await db.fetchone()
    user_tg_id = user_row.get("tg_id") if user_row else None
    user_role = user_row.get("role") if user_row else None
    user_manager_phone = user_row.get("phone_manager") if user_row else None
    user_full_name = user_row.get("full_name") if user_row else ""
    user_phone = user_row.get("phone") if user_row else ""
    user_birth_date = user_row.get("birth_date") if user_row else ""
    user_department = user_row.get("department") if user_row else ""

    # --- Получаем названия отделов ---
    # --- Преобразуем ID отделов в их значения ---
    # Берём department из запроса (data), а не из базы
    # Получаем названия отделов пользователя из таблицы users_dep
    await db.execute("""
        SELECT d.value
        FROM users_dep ud
        JOIN department d ON ud.dep_id = d.id
        WHERE ud.user_id = %s
    """, (emp_id,))
    dep_rows = await db.fetchall()
    dep_values = [row["value"] for row in dep_rows] if dep_rows else []

    departments_str = ", ".join(dep_values) if dep_values else "нет"

    # Получаем список чатов пользователя
    await db.execute("""
        SELECT c.value AS chat_name
        FROM user_chats uc
        JOIN chats c ON uc.chat_id = c.id
        WHERE uc.user_id=%s
    """, (emp_id,))
    chat_rows = await db.fetchall()
    chat_names = [row["chat_name"] for row in chat_rows]

    recipients = set()

    # 1. Уведомляем самого пользователя
    if user_tg_id:
        recipients.add(user_tg_id)

    await db.execute("SELECT is_manager FROM roles WHERE value=%s", (user_role.lower(),))
    role_manager = await db.fetchone()
    is_manager = bool(role_manager['is_manager']) if role_manager else False

    # 2. Если пользователь не руководитель, уведомляем его менеджера
    if user_role and not is_manager and user_manager_phone:
        await db.execute("SELECT tg_id FROM users_managers WHERE phone=%s", (user_manager_phone,))
        mgr_row = await db.fetchone()
        if mgr_row and mgr_row.get("tg_id"):
            recipients.add(mgr_row.get("tg_id"))

    # 3. Уведомляем всех директоров
    await db.execute("SELECT tg_id FROM users_managers WHERE LOWER(role)='директор'")
    directors = await db.fetchall()
    for dir_row in directors:
        if dir_row.get("tg_id"):
            recipients.add(dir_row.get("tg_id"))

    # --- Отправляем уведомления с данными ---
    for tg_id in recipients:
        try:
            await send_message_editing(
                user_tg_id=tg_id,  # исправлено на текущего получателя
                full_name=user_full_name,
                phone=user_phone,
                birth_date=user_birth_date,
                role=user_role,
                department=departments_str,
                chats=chat_names
            )
            print(f"Уведомление отправлено {tg_id}")
        except Exception as e:
            print(f"⚠ Не удалось уведомить {tg_id}: {e}")

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


    # Если пользователь не руководитель и не директор — уведомляем его руководителя
    # Проверяем, что роль не руководящая и не директор
    await db.execute("SELECT is_manager FROM roles WHERE LOWER(value)=%s", (role.lower(),))
    role_info = await db.fetchone()
    is_manager = bool(role_info['is_manager']) if role_info and 'is_manager' in role_info else False

    if not is_manager and role.lower() != 'директор' and user_row.get("phone_manager"):
        # Ищем руководителя по телефону
        await db.execute("""
            SELECT um.tg_id, um.full_name 
            FROM users_managers um
            JOIN roles r ON um.role = r.value
            WHERE um.phone = %s 
            AND r.is_manager = 1 
            AND um.tg_id IS NOT NULL
        """, (user_row["phone_manager"],))
        manager_row = await db.fetchone()
        if manager_row:
            try:
                await notify_manager_fired(
                    manager_row["tg_id"],
                    full_name,   # имя уволенного сотрудника
                    role,
                    department
                )
                print(f"Руководитель {manager_row['full_name']} уведомлен об увольнении {full_name}")
            except Exception as e:
                print(f"Не удалось уведомить руководителя {manager_row['full_name']}: {e}")

        # --- Получаем всех директоров и уведомляем ---
    await db.execute("SELECT tg_id, full_name, department, role FROM users_managers WHERE LOWER(role) IN ('директор', 'admin') AND tg_id IS NOT NULL")
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
