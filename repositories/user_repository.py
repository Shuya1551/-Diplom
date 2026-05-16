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

# ========== АДМИНИСТРАТИВНЫЕ ФУНКЦИИ ==========

def get_all_users():
    """Возвращает список всех пользователей с информацией о роли."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.username, u.email, r.name as role, u.is_active, u.created_at, u.last_login
            FROM users u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.id
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def create_user(username, password_hash, email, role_id, is_active=True):
    """Создаёт нового пользователя. Возвращает ID или None."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, password_hash, email, role_id, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (username, password_hash, email, role_id, is_active))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return user_id
    except Exception as e:
        print(f"Ошибка создания пользователя: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def update_user(user_id, email=None, role_id=None, is_active=None):
    """Обновляет поля пользователя. Возвращает True/False."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        updates = []
        params = []
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if role_id is not None:
            updates.append("role_id = %s")
            params.append(role_id)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)
        if not updates:
            return True
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, params)
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка обновления пользователя: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

def get_role_id_by_name(role_name):
    """Возвращает ID роли по её имени (user, manager, admin)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None
    finally:
        if conn:
            return_connection(conn)

def delete_user(user_id):
    """Удаляет пользователя."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка удаления пользователя: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

def change_password(user_id, new_password_hash):
    """Обновляет пароль пользователя."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, user_id))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка смены пароля: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

def get_roles():
    """Возвращает список всех ролей (id, name)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM roles ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

