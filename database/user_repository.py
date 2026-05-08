"""
Репозиторий для работы с пользователями (аутентификация, получение роли).
"""

import bcrypt
from database.db_connection import get_connection, return_connection

def authenticate_user(username, password):
    """
    Проверяет логин и пароль.
    Возвращает словарь с данными пользователя (id, username, role) или None.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Запрос с JOIN для получения роли
        cur.execute("""
            SELECT u.id, u.username, u.password_hash, r.name as role
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = %s AND u.is_active = TRUE
        """, (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }
        return None
    except Exception as e:
        print(f"Ошибка аутентификации: {e}")
        return None
    finally:
        if conn:
            return_connection(conn)

def get_user_role(user_id):
    """Возвращает название роли пользователя по id."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.name FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """, (user_id,))
        role = cur.fetchone()
        cur.close()
        return role[0] if role else None
    finally:
        if conn:
            return_connection(conn)

