для начала создаем виртуальную среду дабы избежать конфликто
python -m venv venv или
python3 -m venv venv или
py -3.13 -m venv venv

Затем запускаем requirements.txt чтобы установить нужные библеотеки. 
pip install -r requirements.txt

Дале загружаем Модель
git clone https://huggingface.co/ai-forever/rugpt3medium_based_on_gpt2

Потом запускаем файл train_model чтобы переобучитьь модель под свои нужды.

И активируем main.py

КОНЕЦ!
Пока так.
