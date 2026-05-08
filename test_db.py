"""
Тестовый скрипт для проверки подключения к базе данных и выполнения простого запроса.
"""

from database.db_connection import init_connection_pool, get_connection, return_connection

def test_connection():
    if not init_connection_pool():
        print("❌ Не удалось инициализировать пул соединений.")
        return
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        print(f"✅ Подключение успешно. В таблице users {count} записей.")
        cur.close()
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
    finally:
        if conn:
            return_connection(conn)
    
    # Не закрываем пул полностью, чтобы можно было использовать дальше

if __name__ == "__main__":
    test_connection()