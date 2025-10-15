import os, hmac, hashlib, urllib.parse, json
from fastapi import Header, HTTPException
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

async def telegram_user(x_demo_user: str = Header(None), x_init_data: str = Header(None)):
    if x_demo_user:
        return {"id": 111111, "username": "serj_test", "tg_id": 1212121223, "full_name": "Сергей Иванович", "role": "директор", "department": "Frontend", "is_demo": True}
    if not x_init_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = dict(urllib.parse.parse_qsl(x_init_data))
    user_info = json.loads(query.get("user", "{}"))

    # вернём словарь пользователя
    return {
        "id": user_info.get("id"),
        "username": user_info.get("username"),
        "tg_id": user_info.get("id"),
        "full_name": f'{user_info.get("first_name","")} {user_info.get("last_name","")}'.strip(),
        "is_demo": False
    }
    # остальной код проверки Telegram initData