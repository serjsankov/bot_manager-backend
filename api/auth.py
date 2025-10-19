import os, hmac, hashlib, urllib.parse, json
from fastapi import Header, HTTPException, Depends
from db.db import get_db_conn
from config import BOT_TOKEN
import urllib.parse, json
from datetime import datetime

def parse_init_data(init_data: str) -> dict:
    params = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    if 'user' in params:
        try:
            params['user'] = json.loads(params['user'])
        except Exception:
            pass
    return params

def verify_init_data(init_data: str) -> dict:
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing init data")
    parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    check_hash = parsed.pop('hash', None)
    if not check_hash:
        raise HTTPException(status_code=401, detail="Missing hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if hmac_hash != check_hash:
        raise HTTPException(status_code=401, detail="Bad init data")
    return parse_init_data(init_data)

async def telegram_user(x_demo_user: str = Header(None), x_init_data: str = Header(None), db=Depends(get_db_conn)):
    if x_demo_user:
        return {
        # "id": 999999,
        # "created_at": "2025-10-18 14:33:46",
        # "gender": "man",
        # "phone_director": "79000000000",
        # "director": "Алла",
        # "phone_manager": "79000000007",
        # "manager": "Сергей",
        # "department": "IT",
        # "role": "руководитель",
        # "birth_date": "1995-10-17",
        "phone": "79000000003",
        "role": "руководитель",
        "full_name": "Сергей",
        "username": "serj_sankov",
        "tg_id": 704861909,
        "status": "approved",
        "is_demo": True
        }
    if not x_init_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    

    # 3️⃣ Парсим initData от Telegram
    query = dict(urllib.parse.parse_qsl(x_init_data))
    user_info = json.loads(query.get("user", "{}"))
    tg_id = user_info.get("id")

    # 4️⃣ Ищем пользователя в базе
    await db.execute("SELECT * FROM users_managers WHERE tg_id=%s", (tg_id,))
    db_user = await db.fetchone()

    if db_user:
        # Пользователь есть в БД
        status = db_user.get("status", "pending")
        role = db_user.get("role")
        full_name = db_user.get("full_name")
        username = db_user.get("username")
        phone = db_user.get("phone")
    else:
        # Новый пользователь — ещё не зарегистрирован
        status = "pending"
        role = None
        full_name = f'{user_info.get("first_name","")} {user_info.get("last_name","")}'.strip()
        username = user_info.get("username")
        phone = None

    return {
        "id": tg_id,
        "username": username,
        "tg_id": tg_id,
        "full_name": full_name,
        "role": role,
        "status": status,
        "phone": phone,
        "is_demo": False
    }
    
    # query = dict(urllib.parse.parse_qsl(x_init_data))
    # user_info = json.loads(query.get("user", "{}"))

    # # вернём словарь пользователя
    # return {
    #     "id": user_info.get("id"),
    #     "username": user_info.get("username"),
    #     "tg_id": user_info.get("id"),
    #     "full_name": f'{user_info.get("first_name","")} {user_info.get("last_name","")}'.strip(),
    #     "is_demo": True
    # }
    # остальной код проверки Telegram initData