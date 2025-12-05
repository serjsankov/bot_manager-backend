from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Header
from db.db import get_db_conn
from pydantic import BaseModel
from services.telegram import notify_manager

router = APIRouter()

# class UserRegister(BaseModel):
#     gender: str
#     phone_director: Optional[str] = None
#     director: Optional[str] = None
#     phone_manager: Optional[str] = None
#     manager: str
#     department: str
#     role: str
#     birth_date: Optional[date] = None
#     phone: Optional[str] = None
#     full_name: str
#     username: str
#     tg_id: int
class UserRegister(BaseModel):
    gender: str
    phone_director: Optional[str] = None
    director: Optional[str] = None
    phone_manager: Optional[str] = None
    manager: Optional[str] = None 
    department: Optional[object]  # может быть строкой или массивом
    role: str
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    full_name: str
    username: str
    tg_id: int


# @router.post("/")
# async def register_user(user: UserRegister, db=Depends(get_db_conn)):
#     # Проверяем существующего пользователя
#     await db.execute(
#         "SELECT id FROM users_managers WHERE username=%s",
#         (user.username,)
#     )
#     existing_user = await db.fetchone()
#     if existing_user:
#         raise HTTPException(400, detail="Пользователь с таким username уже существует")

#     # Проверка руководителя, если пользователь не руководитель
#     if (user.role or "").lower() != "руководитель":
#         await db.execute(
#             """
#             SELECT id, phone FROM users_managers 
#             WHERE phone = %s AND LOWER(role) = 'руководитель' AND status = 'approved'
#             """,
#             (user.phone_manager,)
#         )
#         manager = await db.fetchone()
#         if not manager:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Руководитель с таким номером не найден или ещё не подтверждён."
#             )
#         if manager["phone"] == user.phone:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Ваш номер не прошёл валидацию."
#             )

#     # Проверка директора, если пользователь руководитель
#     if (user.role or "").lower() == "руководитель":
#         await db.execute(
#             """
#             SELECT id FROM users_managers 
#             WHERE phone = %s AND LOWER(role) = 'директор'
#             """,
#             (user.phone_director,)
#         )
#         director = await db.fetchone()
#         if not director:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Директор с таким номером не найден"
#             )
#     # Вставляем нового пользователя
#     await db.execute(
#         """
#         INSERT INTO users_managers 
#         (gender, phone_director, director, phone_manager, manager, department, role, birth_date, phone, full_name, username, tg_id)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """,
#         (
#             user.gender,
#             user.phone_director,
#             user.director,
#             user.phone_manager,
#             user.manager,
#             user.department,
#             user.role,
#             user.birth_date,       # если None, mysql вставит NULL
#             user.phone,
#             user.full_name,
#             user.username,
#             user.tg_id
#         )
#     )
#     await db.connection.commit()  # commit через соединение
#     user_id = db.lastrowid

#     await db.execute("SELECT tg_id FROM users_managers WHERE full_name=%s", (user.manager))
#     manager = await db.fetchone()

#     await db.execute("SELECT tg_id FROM users_managers WHERE LOWER(role)=%s", ("директор",))
#     director = await db.fetchone()

#     if director:
#         await notify_manager(director["tg_id"], user.full_name, user.role, user.department)

#     if manager and manager["tg_id"]:
#         await notify_manager(manager["tg_id"], user.full_name, user.role, user.department)


#     return {"msg": "Пользователь зарегистрирован", "user_id": user_id}

@router.post("/")
async def register_user(user: UserRegister, db=Depends(get_db_conn)):
    # Проверяем существующего пользователя
    await db.execute("SELECT id FROM users_managers WHERE username=%s", (user.username,))
    existing_user = await db.fetchone()
    if existing_user:
        raise HTTPException(400, detail="Пользователь с таким username уже существует")

    role_lower = (user.role or "").lower()
    # Получаем значение is_manager из БД
    await db.execute("SELECT is_manager FROM roles WHERE value = %s", (role_lower,))
    row = await db.fetchone()  # вернёт словарь типа {'is_manager': 1} или None

    # Преобразуем в булево значение
    is_manager = bool(row['is_manager']) if row and 'is_manager' in row else False

    # Проверка руководителя для обычного сотрудника
    if not is_manager:
        await db.execute("""
            SELECT u.id, u.phone, u.full_name
            FROM users_managers u
            JOIN roles r ON u.role = r.value
            WHERE u.phone = %s
                AND r.is_manager = 1
                AND u.status = 'approved'
        """, (user.phone_manager,))
        manager = await db.fetchone()
        if not manager:
            raise HTTPException(400, detail="Руководитель с таким номером не найден или не подтверждён")
        manager_name = manager["full_name"] # <-- имя берем из БД
        if manager["phone"] == user.phone:
            raise HTTPException(400, detail="Ваш номер не прошёл валидацию.")

    else:
         # руководитель: подставляем свои данные
        manager_name = user.full_name

    # Проверка директора для руководителя
    if is_manager:
        await db.execute("""
            SELECT id FROM users_managers 
            WHERE phone = %s AND LOWER(role) = 'директор'
        """, (user.phone_director,))
        director = await db.fetchone()
        if not director:
            raise HTTPException(400, detail="Директор с таким номером не найден")

    # --- Вставка нового пользователя ---
    await db.execute("""
        INSERT INTO users_managers 
        (gender, phone_director, director, phone_manager, manager, department, role, birth_date, phone, full_name, username, tg_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user.gender,
        user.phone_director,
        user.director,
        user.phone_manager,
        manager_name,
        None if is_manager else user.department,  # руководитель отдел не сохраняет напрямую
        user.role,
        user.birth_date,
        user.phone,
        user.full_name,
        user.username,
        user.tg_id
    ))
    await db.connection.commit()
    user_id = db.lastrowid

    # --- Добавляем связь с отделами ---
    if is_manager:
        # ожидаем список ID отделов
        department_ids = user.department if isinstance(user.department, list) else [user.department]
    else:
        # обычный сотрудник, одна строка → получаем id отдела
        await db.execute("SELECT id FROM department WHERE value=%s", (user.department,))
        dep_row = await db.fetchone()
        department_ids = [dep_row["id"]] if dep_row else []

    for dep_id in department_ids:
        await db.execute("INSERT INTO users_dep (user_id, dep_id) VALUES (%s, %s)", (user_id, dep_id))
    await db.connection.commit()

    # --- Получаем названия отделов для уведомления ---
    await db.execute("""
        SELECT d.value
        FROM users_dep ud
        JOIN department d ON ud.dep_id = d.id
        WHERE ud.user_id = %s
    """, (user_id,))
    dep_rows = await db.fetchall()
    dep_values = [row["value"] for row in dep_rows] if dep_rows else []

    departments_str = ", ".join(dep_values) if dep_values else "нет"

    # --- Уведомляем ---
    # if not is_manager:
    #     await db.execute("SELECT tg_id FROM users_managers WHERE full_name=%s", (user.manager,))
    #     manager = await db.fetchone()
    #     if manager and manager.get("tg_id"):
    #         await notify_manager(manager["tg_id"], user.full_name, user.role, departments_str)

    # await db.execute("SELECT tg_id FROM users_managers WHERE LOWER(role)=%s", ("директор",))
    # director = await db.fetchone()
    # if director:
    #     await notify_manager(director["tg_id"], user.full_name, user.role, departments_str)

    # --- Уведомляем руководителя (если обычный сотрудник) ---
    if not is_manager:
        await db.execute("""
            SELECT tg_id 
            FROM users_managers 
            WHERE full_name=%s AND status='approved'
        """, (user.manager,))
        manager = await db.fetchone()
        if manager and manager.get("tg_id"):
            await notify_manager(manager["tg_id"], user.full_name, user.role, departments_str)
    # --- Уведомляем всех директоров и всех с ролью admin ---
    await db.execute("""
        SELECT tg_id 
        FROM users_managers 
        WHERE status='approved' AND (LOWER(role)='директор' OR LOWER(role)='admin')
    """)
    rows = await db.fetchall()
    for row in rows:
        if row.get("tg_id"):
            await notify_manager(row["tg_id"], user.full_name, user.role, departments_str)

    return {"msg": "Пользователь зарегистрирован", "user_id": user_id}

@router.post("/director")
async def register_director(user: UserRegister, db=Depends(get_db_conn)):
    # Проверка на существующего пользователя по username
    await db.execute("SELECT id FROM users_managers WHERE username=%s", (user.username,))
    existing_user = await db.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")

    # Вставка нового директора
    await db.execute("""
        INSERT INTO users_managers 
        (gender, phone_director, director, phone_manager, manager, department, role, birth_date, phone, full_name, username, tg_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user.gender,
        user.phone_director,
        user.director,
        user.phone_manager,
        user.manager,
        None,            # отдел для директора не нужен
        "директор",      # роль фиксированная
        user.birth_date,
        user.phone,
        user.full_name,
        user.username,
        user.tg_id,
        "approved" 
    ))
    await db.connection.commit()
    user_id = db.lastrowid

    # Можно сразу уведомить самого директора или других сотрудников, если нужно
    # await notify_manager(...)

        # Возвращаем всех директоров
    await db.execute("""
        SELECT *
        FROM users_managers
        WHERE role = 'директор'
        ORDER BY id DESC
    """)
    directors = await db.fetchall()

    return {
        "msg": "Директор зарегистрирован",
        "directors": directors
    }
