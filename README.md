# Генератор новостей из плана мероприятий (нейросетевой)

## Быстрый старт

1. **Создать и активировать виртуальное окружение** (выберите подходящую команду для вашей системы):

python -m venv venv
# или
python3 -m venv venv
# или
py -3.13 -m venv venv

2. **Активировать окружение:

Windows: venv\Scripts\activate
Linux/macOS: source venv/bin/activate

3. **Установить зависимости:

pip install -r requirements.txt

4. **Создать базу данных PostgreSQL (news_generator_db) и выполнить дамп (файл news_generator_db.sql):

psql -U postgres -c "CREATE DATABASE news_generator_db;"
psql -U postgres -d news_generator_db -f news_generator_db.sql

5. **Запустить приложение:

bash
python main.py

Учётные данные по умолчанию
Логин: admin

Пароль: admin123

Примечания
Папка с дообученной моделью (finetuned_rugpt3) должна находиться в корне проекта.

Файлы city.csv и category.csv (необязательные) при наличии добавляют подсказки в поля ввода.
