# Генератор новостей из плана мероприятий (нейросетевой)

## Быстрый старт

1. ** Клонирование репозитория

2. **Создание и активация виртуального окружения

python -m venv venv
# или
python3 -m venv venv
# или
py -3.13 -m venv venv

3. **Активировать окружение:

Windows: venv\Scripts\activate
Linux/macOS: source venv/bin/activate

4. **Установить зависимости:

pip install -r requirements.txt

5. **Запустить приложение:

python main.py

Учётные данные по умолчанию
Логин: admin

Пароль: admin123

Примечания
Папка с дообученной моделями (ruGPT3medium_based_on_gpt2, ruGPT3_manual_finetuned и ruGPT3_finetuned_advanced) должны находиться в корне проекта.

Файлы city.csv и category.csv (необязательные) при наличии добавляют подсказки в поля ввода.
