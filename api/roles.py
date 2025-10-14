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
        "INSERT INTO roles (value) VALUES (%s)",
        (data["value"],)
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

@router.post("/delete")
async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    role_id = data.pop("id", None)

    if not role_id:
        return {"error": "id is required"}

    await db.execute("DELETE FROM roles WHERE id=%s", (role_id,))

    await db.execute("DELETE FROM role_chat WHERE role_id=%s", (role_id))
    await db.execute("DELETE FROM role_dep WHERE role_id=%s", (role_id))

    # return {"status": "ok", "deleted_id": emp_id}
    await db.execute("SELECT * FROM roles")
    users = await db.fetchall()
    return users

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

