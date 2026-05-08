import psycopg2
import bcrypt

DB_NAME = "news_generator_db"
DB_USER = "postgres"
DB_PASSWORD = "0"
DB_HOST = "localhost"

def init_database():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Выполняем SQL-схему (читаем файл)
    with open("db_schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cur.execute(schema_sql)
    
    # Добавляем начальные роли
    cur.execute("INSERT INTO roles (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                ("admin", "Полный доступ"))
    cur.execute("INSERT INTO roles (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                ("manager", "Управление мероприятиями и генерацией"))
    cur.execute("INSERT INTO roles (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                ("user", "Только просмотр"))
    
    # Создаём администратора (пароль: admin123, захеширован)
    admin_pass = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    cur.execute("""
        INSERT INTO users (username, password_hash, email, role_id) 
        VALUES (%s, %s, %s, (SELECT id FROM roles WHERE name='admin'))
        ON CONFLICT (username) DO NOTHING
    """, ("admin", admin_pass, "admin@example.com"))
    
    # Добавляем шаблон по умолчанию
    cur.execute("""
        INSERT INTO templates (name, template_text, is_default) 
        VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING
    """, ("standard", "{{ date }} в {{ location }} состоялось мероприятие «{{ title }}». Спикер {{ speaker }} рассказал о {{ description }}.", True))
    
    # Добавляем настройки
    cur.execute("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) ON CONFLICT (setting_key) DO NOTHING",
                ("model_name", "sberbank-ai/ruT5-base"))
    cur.execute("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) ON CONFLICT (setting_key) DO NOTHING",
                ("max_length", "256"))
    
    cur.close()
    conn.close()
    print("База данных инициализирована успешно.")

if __name__ == "__main__":
    init_database()