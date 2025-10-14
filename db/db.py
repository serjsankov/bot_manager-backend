import aiomysql
from config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT
from dotenv import load_dotenv

load_dotenv()

DB_USER = DB_USER
DB_PASS = DB_PASS
DB_HOST = DB_HOST
DB_NAME = DB_NAME
DB_PORT = DB_PORT

pool = None

async def init_db_pool():
    global pool
    pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        autocommit=True
    )

async def get_db_conn():
    if pool is None:
        raise RuntimeError("DB pool is not initialized. Call init_db_pool first.")
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            yield cur