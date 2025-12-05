from db.db import get_db_conn

async def add_chat_to_db(value: str, link: str, group_id: str, tg_id: int) -> bool:
    """
    Добавляет чат в базу данных, если его ещё нет.
    Возвращает:
        True  - если чат был добавлен
        False - если чат уже существует
    """
    async for conn in get_db_conn():
        # Проверяем, существует ли чат по group_id
        await conn.execute("SELECT id FROM chats WHERE group_id = %s", (group_id,))
        existing_chat = await conn.fetchone()

        if existing_chat:
            # Чат уже есть
            return False

        # Добавляем новый чат
        await conn.execute(
            "INSERT INTO chats (value, group_id, link) VALUES (%s, %s, %s)",
            (value, group_id, link)
        )

        # Получаем ID нового чата
        await conn.execute("SELECT LAST_INSERT_ID() AS id")
        new_chat_row = await conn.fetchone()
        new_chat_id = new_chat_row["id"]

        # Находим пользователя по tg_id
        await conn.execute("SELECT id FROM users_managers WHERE tg_id=%s", (tg_id,))
        user_row = await conn.fetchone()

        if not user_row:
            print(f"⚠️ Пользователь с tg_id={tg_id} не найден")
            return True  # чат добавлен, но пользователь не найден

        user_id = user_row["id"]

        # Вставляем в user_chats
        await conn.execute(
            "INSERT IGNORE INTO user_chats (chat_id, user_id) VALUES (%s, %s)",
            (new_chat_id, user_id)
        )

        print(f"✅ Чат {new_chat_id} добавлен и связан с пользователем {user_id}")
        return True