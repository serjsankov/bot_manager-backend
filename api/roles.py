from fastapi import APIRouter, Depends, Request, HTTPException, Header
from db.db import get_db_conn
from .auth import telegram_user

router = APIRouter()

@router.get("/")
async def list_roles(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM roles")  # ⚡ execute
    rows = await db.fetchall()                   # ⚡ fetchall
    return rows                                  # DictCursor уже возвращает словари

@router.post("/")
async def create_roles(data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    # 1. Создаем новую роль
    await db.execute(
        "INSERT INTO roles (value, is_manager) VALUES (%s, %s)",
        (data["value"], data["is_manager"])
    )
    
    # 2. Получаем ID новой роли
    await db.execute("SELECT LAST_INSERT_ID() AS role_id")
    row = await db.fetchone()
    role_id = row["role_id"]
    
    # 3. Связь с чатами
    chat_ids = data.get("chat_ids", [])
    if chat_ids:
        values = [(role_id, chat_id) for chat_id in chat_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_chat (role_id, chat_id) VALUES (%s, %s)",
            values
        )
    
    # 4. Связь с департаментами
    dep_ids = data.get("dep_ids", [])
    if dep_ids:
        values = [(role_id, dep_id) for dep_id in dep_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_dep (role_id, dep_id) VALUES (%s, %s)",
            values
        )
    
    # 5. Возвращаем все роли (опционально)
    await db.execute("SELECT * FROM roles")
    rows = await db.fetchall()
    return rows

# @router.post("/delete")
# async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
#     data = await request.json()
#     role_id = data.pop("id", None)

#     if not role_id:
#         return {"error": "id is required"}

#     await db.execute("DELETE FROM roles WHERE id=%s", (role_id,))

#     await db.execute("DELETE FROM role_chat WHERE role_id=%s", (role_id,))
#     await db.execute("DELETE FROM role_dep WHERE role_id=%s", (role_id,))

#     # return {"status": "ok", "deleted_id": emp_id}
#     await db.execute("SELECT * FROM roles")
#     users = await db.fetchall()
#     return users
@router.post("/delete")
async def delete_role(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    role_id = data.get("id")
    new_role_val = data.get("new_role_val")

    if not role_id:
        return {"error": True, "message": "Не указан id должности"}

    new_role_id = None
    if new_role_val:
        await db.execute("SELECT id FROM roles WHERE value=%s", (new_role_val,))
        new_role = await db.fetchone()
        if new_role:
            new_role_id = new_role["id"]
        else:
            return {"error": True, "message": f"Должность '{new_role_val}' не найдена"}

    if not role_id:
        return {"error": True, "message": "Не указан id должности"}

    # Получаем старую должность
    await db.execute("SELECT value FROM roles WHERE id=%s", (role_id,))
    old_role = await db.fetchone()
    if not old_role:
        return {"error": True, "message": "Должность не найдена"}

    old_role_name = old_role["value"]

    # Проверяем пользователей с этой должностью
    await db.execute(
        "SELECT id, tg_id, full_name, username FROM users_managers WHERE LOWER(role)=LOWER(%s)",
        (old_role_name,)
    )
    users_in_role = await db.fetchall()

    # Проверяем связи с чатами
    await db.execute(
        """
        SELECT c.id, c.value
        FROM role_chat rc
        JOIN chats c ON c.id = rc.chat_id
        WHERE rc.role_id=%s
        """,
        (role_id,)
    )
    chats_with_role = await db.fetchall()

    # Проверяем связи с отделами
    await db.execute(
        """
        SELECT d.id, d.value
        FROM role_dep rd
        JOIN department d ON d.id = rd.dep_id
        WHERE rd.role_id=%s
        """,
        (role_id,)
    )
    deps_with_role = await db.fetchall()

    # Если должность используется где-то — не удаляем, просим выбрать новую
    if (users_in_role or chats_with_role or deps_with_role) and not new_role_id:
        # Возвращаем список других должностей для переноса
        await db.execute("SELECT * FROM roles WHERE id != %s", (role_id,))
        other_roles = await db.fetchall()

        message_parts = ["Эта должность используется в следующих местах:"]

        if users_in_role:
            message_parts.append("\nПользователи:")
            message_parts.extend(f"- {u['full_name']}" for u in users_in_role)

        if chats_with_role:
            message_parts.append("\nЧаты:")
            message_parts.extend(f"- {c['value']}" for c in chats_with_role)

        if deps_with_role:
            message_parts.append("\nОтделы:")
            message_parts.extend(f"- {d['value']}" for d in deps_with_role)

        message = "\n".join(message_parts)

        return {
            "error": True,
            "message": message,
            "users": users_in_role,
            "chats": chats_with_role,
            "departments": deps_with_role,
            "other_roles": other_roles
        }

    # Если указан перенос на другую должность
    if new_role_id:
        await db.execute("SELECT value FROM roles WHERE id=%s", (new_role_id,))
        new_role = await db.fetchone()

        if not new_role:
            return {"error": True, "message": "Новая должность не найдена"}

        new_role_name = new_role["value"]

        # Переносим пользователей
        await db.execute(
            "UPDATE users_managers SET role=%s WHERE LOWER(role)=LOWER(%s)",
            (new_role_name, old_role_name)
        )

        # Переносим связи с чатами
        # await db.execute(
        #     "UPDATE role_chat SET role_id=%s WHERE role_id=%s",
        #     (new_role_id, role_id)
        # )
        await db.execute(
            "UPDATE role_chat rc "
            "LEFT JOIN role_chat rc2 ON rc.chat_id = rc2.chat_id AND rc2.role_id = %s "
            "SET rc.role_id = %s "
            "WHERE rc.role_id = %s AND rc2.role_id IS NULL",
            (new_role_id, new_role_id, role_id)
        )

        # Переносим связи с отделами
        # await db.execute(
        #     "UPDATE role_dep SET role_id=%s WHERE role_id=%s",
        #     (new_role_id, role_id)
        # )
        await db.execute(
            "UPDATE role_dep rd "
            "LEFT JOIN role_dep rd2 ON rd.dep_id = rd2.dep_id AND rd2.role_id = %s "
            "SET rd.role_id = %s "
            "WHERE rd.role_id = %s AND rd2.role_id IS NULL",
            (new_role_id, new_role_id, role_id)
        )

    # Удаляем старую должность
    await db.execute("DELETE FROM roles WHERE id=%s", (role_id,))

    # Возвращаем обновлённый список должностей
    await db.execute("SELECT * FROM roles")
    roles = await db.fetchall()

    print(f"Удалена должность ID={role_id}, перенесено в {new_role_id}")
    return {"status": "ok", "message": "Должность успешно удалена", "roles": roles}

@router.post("/edit")
async def change_role( request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data_ = await request.json()
    role_id = data_.pop("id", None)
    if not role_id:
        return {"error": "id is required"}

    role_id_ = data.get("id")
    value = data.get("value")
    chat_ids = data.get("chat_ids", [])
    dep_ids = data.get("dep_ids", [])

    await db.execute("SELECT value FROM roles WHERE id=%s", (role_id_,))
    old_role = await db.fetchone()

    await db.execute("UPDATE users_managers SET role = %s WHERE LOWER(role) = LOWER(%s) """, (value.lower(), old_role["value"]))

    await db.execute("UPDATE roles SET value=%s WHERE id=%s", (value, role_id_))

    # 2. Связь с чатами
    if chat_ids:
        # 1. Вставляем новые связи (игнорируя дубликаты)
        values = [(role_id, chat_id) for chat_id in chat_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_chat (role_id, chat_id) VALUES (%s, %s)",
            values
        )
        # 2. Удаляем все лишние связи, которых нет в новом списке chat_ids
        await db.execute(
            "DELETE FROM role_chat WHERE role_id = %s AND chat_id NOT IN %s",
            (role_id, tuple(chat_ids))
        )

    # 3. Связь с отделами
    if dep_ids:
        # 1. Вставляем новые связи (игнорируя дубликаты)
        values = [(role_id, dep_id) for dep_id in dep_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_dep (role_id, dep_id) VALUES (%s, %s)",
            values
        )
        # 2. Удаляем все лишние связи, которых нет в новом списке dep_ids
        await db.execute(
            "DELETE FROM role_dep WHERE role_id = %s AND dep_id NOT IN %s",
            (role_id, tuple(dep_ids))
        )

    # получаем саму роль
    await db.execute("SELECT * FROM roles WHERE id=%s", (role_id_,))
    role = await db.fetchone()

    await db.execute("SELECT * FROM roles")
    roles = await db.fetchall()

    # чаты
    await db.execute("""
        SELECT c.id, c.value 
        FROM role_chat rc
        JOIN chats c ON c.id = rc.chat_id
        WHERE rc.role_id=%s
    """, (role_id_,))
    chats = await db.fetchall()

    # отделы
    await db.execute("""
        SELECT d.id, d.value 
        FROM role_dep rd
        JOIN department d ON d.id = rd.dep_id
        WHERE rd.role_id=%s
    """, (role_id_,))
    deps = await db.fetchall()

    return roles

@router.post("/data")
async def all_data_role( request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    role_id_ = data.get("id")

    # получаем саму роль
    await db.execute("SELECT * FROM roles WHERE id=%s", (role_id_,))
    role = await db.fetchone()

    # чаты
    await db.execute("""
        SELECT c.id, c.value 
        FROM role_chat rc
        JOIN chats c ON c.id = rc.chat_id
        WHERE rc.role_id=%s
    """, (role_id_,))
    chats = await db.fetchall()
    # преобразуем в нужный формат
    chat_ids = [{"id": row["id"]} for row in chats]

    # отделы
    await db.execute("""
        SELECT d.id, d.value 
        FROM role_dep rd
        JOIN department d ON d.id = rd.dep_id
        WHERE rd.role_id=%s
    """, (role_id_,))
    deps = await db.fetchall()
    dep_ids = [{"id": row["id"]} for row in deps]

    return {
        "role": role,
        "chat_ids": chat_ids,
        "dep_ids": dep_ids
    }

