"""
Репозиторий для работы с логами генерации (таблица generation_logs).
"""

from database.db_connection import get_connection, return_connection

def get_all_generation_logs(limit=100):
    """Возвращает последние логи генерации с информацией о пользователе и плане."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT gl.id, gl.timestamp, u.username, ep.title, gl.success, gl.inference_time_ms, gl.error_message
            FROM generation_logs gl
            LEFT JOIN users u ON gl.user_id = u.id
            LEFT JOIN event_plans ep ON gl.event_plan_id = ep.id
            ORDER BY gl.timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        if conn:
            return_connection(conn)

def get_generation_stats():
    """Возвращает статистику: общее число генераций, успешных, среднее время."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                AVG(inference_time_ms) as avg_time_ms
            FROM generation_logs
        """)
        row = cur.fetchone()
        cur.close()
        return {
            'total': row[0] or 0,
            'successful': row[1] or 0,
            'avg_time_ms': round(row[2], 2) if row[2] else 0
        }
    finally:
        if conn:
            return_connection(conn)

def log_generation(event_plan_id, user_id, prompt_text, generated_text, success, error_message=None, inference_time_ms=None):
    """Логирует попытку генерации."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO generation_logs (event_plan_id, user_id, timestamp, prompt_text, generated_text, success, error_message, inference_time_ms)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s)
        """, (event_plan_id, user_id, prompt_text, generated_text, success, error_message, inference_time_ms))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Ошибка логирования: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            return_connection(conn)