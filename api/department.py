from fastapi import APIRouter, Depends, HTTPException, Header, Request
from db.db import get_db_conn
from .auth import telegram_user

router = APIRouter()

@router.get("/")
async def list_department(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM department")  # ⚡ execute
    rows = await db.fetchall()                   # ⚡ fetchall
    return rows                                  # DictCursor уже возвращает словари

@router.post("/")
async def create_department(data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    # 1. Создаем новую роль
    await db.execute(
        "INSERT INTO department (value) VALUES (%s)",
        (data["value"],)
    )
    
    # 2. Получаем ID нового отдела
    await db.execute("SELECT LAST_INSERT_ID() AS dep_id")
    row = await db.fetchone()
    dep_id = row["dep_id"]
    
    # 3. Связь с ролями
    role_ids = data.get("role_ids", [])
    if role_ids:
        values = [(dep_id, role_id) for role_id in role_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_dep (dep_id, role_id) VALUES (%s, %s)",
            values
        )
    
    # 5. Возвращаем все роли (опционально)
    await db.execute("SELECT * FROM department")
    rows = await db.fetchall()
    return rows

@router.post("/delete")
async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    dep_id = data.pop("id", None)

    if not dep_id:
        return {"error": "id is required"}

    await db.execute("DELETE FROM department WHERE id=%s", (dep_id,))

    await db.execute("DELETE FROM role_dep WHERE dep_id=%s", (dep_id))

    # return {"status": "ok", "deleted_id": emp_id}
    await db.execute("SELECT * FROM department")
    departments = await db.fetchall()
    return departments

@router.post("/data")
async def all_data_role( request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    dep_id = data.get("id")

    # получаем саму роль
    await db.execute("SELECT * FROM department WHERE id=%s", (dep_id,))
    dep = await db.fetchone()

    # чаты
    # await db.execute("""
    #     SELECT c.id, c.value 
    #     FROM role_dep rc
    #     JOIN department c ON c.id = rc.dep_id
    #     WHERE rc.dep_id=%s
    # """, (dep_id,))

    await db.execute("""
        SELECT r.id, r.value
        FROM role_dep rd
        JOIN roles r ON r.id = rd.role_id
        WHERE rd.dep_id = %s
    """, (dep_id,))
    
    roles = await db.fetchall()
    # преобразуем в нужный формат
    role_ids = [{"id": row["id"]} for row in roles]

    return {
        "dep": dep,
        "role_ids": role_ids,
    }

@router.post("/edit")
async def change_role( request: Request, data: dict, user=Depends(telegram_user), db=Depends(get_db_conn)):
    dep_id = data.get("id")

    value = data.get("value")
    role_ids = data.get("role_ids", [])

    await db.execute("UPDATE department SET value=%s WHERE id=%s", (value, dep_id))

    # 2. Связь с чатами
    if role_ids:
        # 1. Вставляем новые связи (игнорируя дубликаты)
        values = [(dep_id, role_id) for role_id in role_ids]
        await db.executemany(
            "INSERT IGNORE INTO role_dep (dep_id, role_id) VALUES (%s, %s)",
            values
        )

        # 2. Удаляем все лишние связи, которых нет в новом списке chat_ids
        await db.execute(
            "DELETE FROM role_chat WHERE role_id = %s AND chat_id NOT IN %s",
            (dep_id, tuple(role_ids))
        )

    await db.execute("SELECT * FROM department")
    deps = await db.fetchall()

    return deps