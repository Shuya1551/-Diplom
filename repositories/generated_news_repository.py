"""
Репозиторий для работы со сгенерированными новостями (таблица generated_news).
"""

from database.db_connection import get_connection, return_connection

def save_generated_news(event_plan_id, generated_text, user_id, rating=None):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO generated_news (event_plan_id, generated_text, generation_date, is_approved, approved_by, rating)
            VALUES (%s, %s, CURRENT_TIMESTAMP, FALSE, %s, %s)
            RETURNING id
        """, (event_plan_id, generated_text, user_id, rating))
        news_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return news_id
    except Exception as e:
        print(f"Ошибка сохранения новости: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            return_connection(conn)

def get_news_by_plan_id(event_plan_id):
    """Возвращает все новости, сгенерированные для данного плана."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, generated_text, generation_date, is_approved, rating
            FROM generated_news
            WHERE event_plan_id = %s
            ORDER BY generation_date DESC
        """, (event_plan_id,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def get_all_generated_news():
    """Возвращает все новости с информацией о плане."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT gn.id, gn.generated_text, gn.generation_date, gn.is_approved, gn.rating,
                   ep.id as plan_id, ep.title as plan_title
            FROM generated_news gn
            JOIN event_plans ep ON gn.event_plan_id = ep.id
            ORDER BY gn.generation_date DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def get_news_by_id(news_id):
    """Возвращает одну новость по ID (полный текст)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, generated_text, generation_date, is_approved, rating, event_plan_id FROM generated_news WHERE id = %s", (news_id,))
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        if conn:
            return_connection(conn)

def get_news_by_user_id(user_id):
    """Возвращает все новости, сгенерированные пользователем, с информацией о плане."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT gn.id, gn.generated_text, gn.generation_date, gn.is_approved, gn.rating,
                   ep.title as plan_title
            FROM generated_news gn
            JOIN event_plans ep ON gn.event_plan_id = ep.id
            WHERE gn.approved_by = %s
            ORDER BY gn.generation_date DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def get_recent_news(limit=5):
    """Возвращает последние сгенерированные новости с краткой информацией."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT gn.id, gn.generated_text, gn.generation_date, ep.title
            FROM generated_news gn
            LEFT JOIN event_plans ep ON gn.event_plan_id = ep.id
            ORDER BY gn.generation_date DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def delete_generated_news(news_id):
    """Удаляет новость по ID."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM generated_news WHERE id = %s", (news_id,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка удаления новости: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)