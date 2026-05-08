"""
Тест аутентификации: проверяем, что пользователь admin может войти.
"""

from database.db_connection import init_connection_pool
from database.user_repository import authenticate_user

def main():
    print("Инициализация пула соединений...")
    if not init_connection_pool():
        print("❌ Не удалось подключиться к БД")
        return
    
    print("Проверка аутентификации admin/admin123...")
    user = authenticate_user("admin", "admin123")
    
    if user:
        print(f"✅ Успешно! User: {user}")
    else:
        print("❌ Ошибка: неверный логин или пароль, либо пользователь не активен")

if __name__ == "__main__":
    main()