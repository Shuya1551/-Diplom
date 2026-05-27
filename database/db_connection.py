"""
Модуль управления подключением к базе данных PostgreSQL.
Использует пул соединений для эффективной работы.
"""

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если есть)
load_dotenv()

# Параметры подключения из переменных окружения или значения по умолчанию
DB_NAME = os.getenv("DB_NAME", "news_generator_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "0")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Глобальный пул соединений
connection_pool = None

def init_connection_pool(min_conn=1, max_conn=10):
    """
    Инициализирует пул соединений с БД.
    Возвращает True при успехе, иначе False.
    """
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            min_conn, max_conn,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Пул соединений с БД успешно создан.")
        return True
    except Exception as e:
        print(f"Ошибка при создании пула соединений: {e}")
        return False

def get_connection():
    """Возвращает соединение из пула."""
    if connection_pool:
        return connection_pool.getconn()
    else:
        raise Exception("Пул соединений не инициализирован. Вызовите init_connection_pool() сначала.")

def return_connection(conn):
    """Возвращает соединение обратно в пул."""
    if connection_pool and conn:
        connection_pool.putconn(conn)

def close_all_connections():
    """Закрывает все соединения в пуле."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Все соединения с БД закрыты.")