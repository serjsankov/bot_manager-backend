from fastapi import APIRouter, Depends, Header, HTTPException
from db.db import get_db_conn
from .auth import telegram_user, parse_init_data  # импортируем утилиты

router = APIRouter()

@router.get("/whoami")
async def whoami(user=Depends(telegram_user), db=Depends(get_db_conn)):
    if user.get("is_demo"):
        return {**user, "is_new": False}

    # Получаем данные пользователя из БД
    await db.execute(
        "SELECT id, username, role, tg_id, phone, phone_manager, status, birth_date, full_name FROM users_managers WHERE tg_id=%s",
        (user["tg_id"],),
    )
    user_data = await db.fetchone()

    if not user_data:
        # Новый пользователь — возвращаем "заглушку"
        return {
            "id": None,
            "username": user.get("username"),
            "tg_id": user.get("tg_id"),
            "role": None,
            "is_new": True,
        }

    # Получаем значение is_manager из таблицы roles
    await db.execute("SELECT is_manager FROM roles WHERE value=%s", (user_data["role"],))
    user_role_bool = await db.fetchone()
    is_manager = bool(user_role_bool['is_manager']) if user_role_bool and 'is_manager' in user_role_bool else False

    user_data["is_new"] = False
    user_data["role_bool"] = is_manager
    return user_data