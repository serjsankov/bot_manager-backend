from fastapi import APIRouter, Depends, HTTPException, Header, Request
from db.db import get_db_conn
from .auth import telegram_user

router = APIRouter()

# @router.get("/")
# async def list_department(user=Depends(telegram_user), db=Depends(get_db_conn)):
#     await db.execute("SELECT full_name, department, role FROM users_managers WHERE tg_id=%s", (user["tg_id"],))
#     user_dep = await db.fetchone()

#     if user_dep["role"] != 'директор':
#         await db.execute("SELECT * FROM department WHERE value=%s", (user_dep["department"],))  # ⚡ execute
#         rows = await db.fetchall()                   # ⚡ fetchall
#         return rows                                  # DictCursor уже возвращает словари
#     else:
#         await db.execute("SELECT * FROM department")  # ⚡ execute
#         rows = await db.fetchall()                   # ⚡ fetchall
#         return rows 
# @router.get("/")
# async def list_department(user=Depends(telegram_user), db=Depends(get_db_conn)):
#     await db.execute(
#         "SELECT full_name, department, role FROM users_managers WHERE tg_id=%s",
#         (user["tg_id"],)
#     )
#     user_dep = await db.fetchone()

#     if not user_dep:
#         return {"error": "Пользователь не найден"}  # обработка отсутствия

#     if user_dep["role"] != 'директор':
#         await db.execute(
#             "SELECT * FROM department WHERE value=%s",
#             (user_dep["department"],)
#         )
#         rows = await db.fetchall()
#         return rows
#     else:
#         await db.execute("SELECT * FROM department")
#         rows = await db.fetchall()
#         return rows
@router.get("/")
async def list_department(user=Depends(telegram_user), db=Depends(get_db_conn)):
    # Получаем информацию о пользователе
    await db.execute(
        "SELECT id, full_name, role FROM users_managers WHERE tg_id=%s",
        (user["tg_id"],)
    )
    user_data = await db.fetchone()

    if not user_data:
        return {"error": "Пользователь не найден"}

    # Если директор — возвращаем все отделы
    if user_data["role"] == 'директор' or user_data["role"] == 'admin':
        await db.execute("SELECT * FROM department")
        rows = await db.fetchall()
        return rows

    # Если не директор — выбираем только отделы, где он руководитель
    await db.execute("""
        SELECT d.*
        FROM department d
        JOIN users_dep ud ON d.id = ud.dep_id
        WHERE ud.user_id = %s
    """, (user_data["id"],))
    rows = await db.fetchall()

    return rows

@router.get("/all")
async def list_department_all(user=Depends(telegram_user), db=Depends(get_db_conn)):
    await db.execute("SELECT * FROM department")  # ⚡ execute
    rows = await db.fetchall()                   # ⚡ fetchall
    return rows 

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

# @router.post("/delete")
# async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
#     data = await request.json()
#     dep_id = data.get("id")  # получаем id отдела

#     if not dep_id:
#         return {"error": "id is required"}

#     # Получаем название отдела
#     await db.execute("SELECT value FROM department WHERE id=%s", (dep_id,))
#     dep = await db.fetchone()

#     if not dep:
#         return {"error": "Department not found"}

#     # Проверяем, есть ли пользователи в этом отделе
#     await db.execute(
#         "SELECT id, tg_id, full_name, username FROM users_managers WHERE LOWER(department) = LOWER(%s)",
#         (dep["value"],)
#     )
#     user_dep = await db.fetchall()

#     # Получаем список всех остальных отделов
#     await db.execute("SELECT * FROM department WHERE id != %s", (dep_id,))
#     other_departments = await db.fetchall()

#     if user_dep:  # если есть пользователи
#         return {
#             "error": "Cannot delete department",
#             "message": "There are users in this department",
#             "users": user_dep,
#             "other_departments": other_departments
#         }

#     # Если пользователей нет — удаляем отдел
#     await db.execute("DELETE FROM department WHERE id=%s", (dep_id,))
#     await db.execute("DELETE FROM role_dep WHERE dep_id=%s", (dep_id,))

#     # Возвращаем обновленный список отделов
#     await db.execute("SELECT * FROM department")
#     departments = await db.fetchall()

#     return {"status": "ok", "departments": departments}
@router.post("/delete")
async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
    data = await request.json()
    dep_id = data.get("id")
    new_dep_id = data.get("new_dep_id")

    if not dep_id:
        return {"error": True, "message": "Не указан id отдела"}

    # Получаем отдел
    await db.execute("SELECT value FROM department WHERE id=%s", (dep_id,))
    old_dep = await db.fetchone()
    if not old_dep:
        return {"error": True, "message": "Отдел не найден"}

    old_dep_name = old_dep["value"]

    # --- Получаем пользователей в этом отделе ---
    await db.execute("""
        SELECT DISTINCT um.id, um.tg_id, um.full_name, um.username
        FROM users_managers um
        LEFT JOIN users_dep ud ON um.id = ud.user_id
        LEFT JOIN department d ON ud.dep_id = d.id
        WHERE LOWER(um.department) = LOWER(%s) OR ud.dep_id = %s
    """, (old_dep_name, dep_id))
    users_in_dep = await db.fetchall()

    # --- Формируем список имён корректно ---
    user_names = [u["full_name"] for u in users_in_dep if u.get("full_name")]

    if users_in_dep and not new_dep_id:
        # Возвращаем список других отделов для переноса
        await db.execute("SELECT * FROM department WHERE id != %s", (dep_id,))
        other_departments = await db.fetchall()

        return {
            "error": True,
            "message": (
                "В этом отделе есть пользователи. Выберите новый отдел для переноса.\n"
                + "\n".join(f"- {name['full_name']}" for name in users_in_dep)
            ),
            "users": users_in_dep,
            "other_departments": other_departments
        }

    # --- Перенос пользователей в новый отдел ---
    if new_dep_id:
        await db.execute("SELECT value FROM department WHERE id=%s", (new_dep_id,))
        new_dep = await db.fetchone()
        if not new_dep:
            return {"error": True, "message": "Новый отдел не найден"}

        new_dep_name = new_dep["value"]

        # Удаляем старые связи в users_dep
        await db.execute("DELETE FROM users_dep WHERE dep_id=%s", (dep_id,))
        # Добавляем новые связи
        for u in users_in_dep:
            await db.execute(
                "INSERT INTO users_dep (user_id, dep_id) VALUES (%s, %s)",
                (u["id"], new_dep_id)
            )

    # --- Удаляем отдел ---
    await db.execute("DELETE FROM department WHERE id=%s", (dep_id,))
    await db.execute("DELETE FROM role_dep WHERE dep_id=%s", (dep_id,))

    # --- Возвращаем актуальный список отделов ---
    await db.execute("SELECT * FROM department")
    departments = await db.fetchall()

    print(f"Удалён отдел ID={dep_id}, перенесено в {new_dep_id}")
    return {"status": "ok", "message": "Отдел успешно удалён", "departments": departments}
# @router.post("/delete")
# async def delete_user(request: Request, user=Depends(telegram_user), db=Depends(get_db_conn)):
#     data = await request.json()
#     dep_id = data.get("id")
#     new_dep_id = data.get("new_dep_id")

#     if not dep_id:
#         return {"error": True, "message": "Не указан id отдела"}

#     # Получаем отдел
#     await db.execute("SELECT value FROM department WHERE id=%s", (dep_id,))
#     old_dep = await db.fetchone()
#     if not old_dep:
#         return {"error": True, "message": "Отдел не найден"}

#     old_dep_name = old_dep["value"]

#     # Проверяем пользователей
#     await db.execute(
#         "SELECT id, tg_id, full_name, username FROM users_managers WHERE LOWER(department)=LOWER(%s)",
#         (old_dep_name,)
#     )
#     users_in_dep = await db.fetchall()

#     if users_in_dep and not new_dep_id:
#         # Возвращаем список других отделов
#         await db.execute("SELECT * FROM department WHERE id != %s", (dep_id,))
#         other_departments = await db.fetchall()

#         return {
#             "error": True,
#              "message": (
#                     "В этом отделе есть пользователи. Выберите новый отдел для переноса.\n"
#                 + "\n".join(f"- {name['full_name']}" for name in users_in_dep)
#             ),
#             "users": users_in_dep,
#             "other_departments": other_departments
#         }

#     # Если нужно переносить пользователей
#     if new_dep_id:
#         await db.execute("SELECT value FROM department WHERE id=%s", (new_dep_id,))
#         new_dep = await db.fetchone()

#         if not new_dep:
#             return {"error": True, "message": "Новый отдел не найден"}

#         new_dep_name = new_dep["value"]

#         # Обновляем пользователей
#         await db.execute(
#             "UPDATE users_managers SET department=%s WHERE LOWER(department)=LOWER(%s)",
#             (new_dep_name, old_dep_name)
#         )

#         # await db.commit()

#             # Удаляем старый отдел
#     await db.execute("DELETE FROM department WHERE id=%s", (dep_id,))
#     await db.execute("DELETE FROM role_dep WHERE dep_id=%s", (dep_id,))
#     # Возвращаем актуальный список отделов
#     await db.execute("SELECT * FROM department")
#     departments = await db.fetchall()

#     print(f"Удалён отдел ID={dep_id}, перенесено в {new_dep_id}")
#     return {"status": "ok", "message": "Отдел успешно удалён", "departments": departments}

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

    await db.execute("SELECT value FROM department WHERE id=%s", (dep_id,))
    old_dep = await db.fetchone()
    await db.execute("UPDATE users_managers SET department=%s WHERE LOWER(department)=LOWER(%s)", (value, old_dep["value"]))

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