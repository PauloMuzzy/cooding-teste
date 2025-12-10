from contextlib import asynccontextmanager
import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
from utils.logger import log_error

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "autocommit": True,
    "pool_name": os.getenv("DB_POOL_NAME", "mypool"),
    "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
}

cnxpool: pooling.MySQLConnectionPool | None = None

def init_pool() -> None:
    global cnxpool
    if cnxpool is None:
        try:
            cnxpool = pooling.MySQLConnectionPool(**DB_CONFIG)
        except mysql.connector.Error as err:
            log_error(f"Erro ao criar pool MySQL: {err}", "database_pool")
            raise

@asynccontextmanager
async def get_db():
    if cnxpool is None:
        init_pool()

    conn = None
    cursor = None
    try:
        conn = cnxpool.get_connection()
        cursor = conn.cursor(dictionary=True)
        yield conn, cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        log_error(f"Erro no banco: {e}", "database_transaction")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
