from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Header
from db.db import get_db_conn
from pydantic import BaseModel
from services.telegram import notify_manager

router = APIRouter()

class UserRegister(BaseModel):
    gender: str
    phone_director: Optional[str] = None
    director: Optional[str] = None
    phone_manager: Optional[str] = None
    manager: str
    department: str
    role: str
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    full_name: str
    username: str
    tg_id: int


@router.post("/")
async def register_user(user: UserRegister, db=Depends(get_db_conn)):
    # Проверяем существующего пользователя
    await db.execute(
        "SELECT id FROM users_managers WHERE username=%s",
        (user.username,)
    )
    existing_user = await db.fetchone()
    if existing_user:
        raise HTTPException(400, detail="Пользователь с таким username уже существует")

    # Проверка руководителя, если пользователь не руководитель
    if (user.role or "").lower() != "руководитель":
        await db.execute(
            """
            SELECT id FROM users_managers 
            WHERE phone = %s AND role = 'руководитель' AND status = 'approved'
            """,
            (user.phone_manager,)
        )
        manager = await db.fetchone()
        if not manager:
            raise HTTPException(
                status_code=400,
                detail="Руководитель с таким номером не найден или ещё не подтверждён"
            )

    # Проверка директора, если пользователь руководитель
    if (user.role or "").lower() == "руководитель":
        await db.execute(
            """
            SELECT id FROM users_managers 
            WHERE phone = %s AND role = 'директор'
            """,
            (user.phone_director,)
        )
        director = await db.fetchone()
        if not director:
            raise HTTPException(
                status_code=400,
                detail="Директор с таким номером не найден"
            )
    # Вставляем нового пользователя
    await db.execute(
        """
        INSERT INTO users_managers 
        (gender, phone_director, director, phone_manager, manager, department, role, birth_date, phone, full_name, username, tg_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user.gender,
            user.phone_director,
            user.director,
            user.phone_manager,
            user.manager,
            user.department,
            user.role,
            user.birth_date,       # если None, mysql вставит NULL
            user.phone,
            user.full_name,
            user.username,
            user.tg_id
        )
    )
    await db.connection.commit()  # commit через соединение
    user_id = db.lastrowid

    await db.execute("SELECT tg_id FROM users_managers WHERE full_name=%s", (user.manager))
    manager = await db.fetchone()

    await db.execute("SELECT tg_id FROM users_managers WHERE role=%s", ("директор"))
    director = await db.fetchone()

    if director:
        await notify_manager(director["tg_id"], user.full_name, user.role, user.department)

    if manager and manager["tg_id"]:
        await notify_manager(manager["tg_id"], user.full_name, user.role, user.department)


    return {"msg": "Пользователь зарегистрирован", "user_id": user_id}

    # Вставляем нового пользователя
    # query_insert = """
    #     INSERT INTO users_managers (full_name, email, birth_date)
    #     VALUES (:full_name, :email, :birth_date)
    # """
    # user_id = await db.execute(query_insert, values=user.dict())

    # return {"msg": "Пользователь зарегистрирован", "user_id": user_id}