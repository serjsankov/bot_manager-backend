from fastapi import APIRouter, Depends, Header, HTTPException
from db.db import get_db_conn
from .auth import telegram_user, parse_init_data  # импортируем утилиты

router = APIRouter()

@router.get("/whoami")
async def whoami(user=Depends(telegram_user), db=Depends(get_db_conn)):
    if user.get("is_demo"):
        return {**user, "is_new": False}

    await db.execute(
        "SELECT id, username, role, tg_id, status FROM users_managers WHERE tg_id=%s",
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

    user_data["is_new"] = False
    return user_data