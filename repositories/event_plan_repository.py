"""
Репозиторий для работы с планами мероприятий.
"""

from database.db_connection import get_connection, return_connection
from datetime import date, time

def create_event_plan(title, event_date, event_time, event_end_time, location, description, speaker, audience, category, created_by):
    """
    Создаёт новый план мероприятия.
    Возвращает ID созданной записи или None при ошибке.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO event_plans 
            (title, event_date, event_time, event_end_time, location, description, speaker, audience, category, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (title, event_date, event_time, event_end_time, location, description, speaker, audience, category, created_by))
        plan_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return plan_id
    except Exception as e:
        print(f"Ошибка при создании плана: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def get_all_event_plans(user_id=None, user_role=None):
    """
    Возвращает список планов мероприятий.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        if user_role == 'admin':
            cur.execute("""
                SELECT id, title, event_date, event_time, event_end_time, location, description, speaker, audience, category, created_by, created_at
                FROM event_plans
                ORDER BY event_date DESC, event_time
            """)
        else:
            cur.execute("""
                SELECT id, title, event_date, event_time, event_end_time, location, description, speaker, audience, category, created_by, created_at
                FROM event_plans
                WHERE created_by = %s
                ORDER BY event_date DESC, event_time
            """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def get_event_plan_by_id(plan_id, user_id=None, user_role=None):
    """
    Возвращает план, если пользователь имеет доступ.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        if user_role == 'admin':
            cur.execute("SELECT * FROM event_plans WHERE id = %s", (plan_id,))
        else:
            cur.execute("SELECT * FROM event_plans WHERE id = %s AND created_by = %s", (plan_id, user_id))
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        if conn:
            return_connection(conn)

def update_event_plan(plan_id, title, event_date, event_time, event_end_time, location, description, speaker, audience, category):
    """Обновляет существующий план."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE event_plans
            SET title=%s, event_date=%s, event_time=%s, event_end_time=%s,
                location=%s, description=%s, speaker=%s, audience=%s, category=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (title, event_date, event_time, event_end_time, location, description, speaker, audience, category, plan_id))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка обновления: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)

def delete_event_plan(plan_id):
    """Удаляет план по ID."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Удаляем логи и новости, связанные с этим планом
        cur.execute("DELETE FROM generation_logs WHERE event_plan_id = %s", (plan_id,))
        cur.execute("DELETE FROM generated_news WHERE event_plan_id = %s", (plan_id,))
        cur.execute("DELETE FROM event_plans WHERE id = %s", (plan_id,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка удаления плана: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)