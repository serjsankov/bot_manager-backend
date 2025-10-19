from db.db import get_db_conn

async def add_chat_to_db(value: str, link: str, group_id: str):
    """
    Добавляет новый чат в таблицу chats.
    """
    async for conn in get_db_conn():
        await conn.execute(
            """
            INSERT INTO chats (value, group_id, link)
            VALUES (%s, %s, %s)
            """,
            (value, group_id, link)
        )