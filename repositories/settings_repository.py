"""
Репозиторий для работы с системными настройками (таблица settings).
"""

from database.db_connection import get_connection, return_connection

def get_setting(key, default=None):
    """Возвращает значение настройки по ключу или default, если не найдена."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else default
    finally:
        if conn:
            return_connection(conn)

def set_setting(key, value, user_id=None):
    """Устанавливает значение настройки. Если ключ существует, обновляет, иначе вставляет."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO settings (setting_key, setting_value, updated_by, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (setting_key) DO UPDATE
            SET setting_value = EXCLUDED.setting_value,
                updated_by = EXCLUDED.updated_by,
                updated_at = CURRENT_TIMESTAMP
        """, (key, value, user_id))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка сохранения настройки {key}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

def get_all_settings():
    """Возвращает словарь всех настроек {key: value}."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT setting_key, setting_value FROM settings")
        rows = cur.fetchall()
        cur.close()
        return {row[0]: row[1] for row in rows}
    finally:
        if conn:
            return_connection(conn)