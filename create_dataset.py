import json
import random
from datetime import datetime, timedelta

# ================== РАСШИРЕННЫЕ СПИСКИ ==================
CITIES = [
    "Москва", "Санкт-Петербург", "Казань", "Новосибирск", "Екатеринбург",
    "Нижний Новгород", "Самара", "Омск", "Челябинск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Пермь", "Воронеж", "Волгоград", "Краснодар",
    "Тюмень", "Иркутск", "Ярославль", "Томск", "Кемерово", "Саратов"
]
FORMATS = ["Очный", "Онлайн", "Гибрид"]
CATEGORIES = [
    "Конференция", "Семинар", "Вебинар", "Мастер-класс", "Хакатон",
    "Лекция", "Выставка", "Фестиваль", "Круглый стол", "Тренинг",
    "Спектакль", "Кинопоказ", "Презентация", "Деловая игра", "Тимбилдинг"
]
TITLE_TEMPLATES = [
    "{} по {}", "{}: {} и будущее", "{} «{}»", "{} на тему «{}»",
    "{} для {}", "{}: от теории к практике", "{} года"
]
TITLE_PARTS1 = [
    "Хакатон", "Конференция", "Семинар", "Вебинар", "Мастер-класс",
    "Лекция", "Выставка", "Фестиваль", "Круглый стол", "Тренинг"
]
TITLE_PARTS2 = [
    "искусственному интеллекту", "машинному обучению", "кибербезопасности",
    "финансовой грамотности", "экологичному развитию", "новым медиа",
    "управлению проектами", "цифровой трансформации", "креативным индустриям",
    "нейротехнологиям", "робототехнике", "коворкингу", "блокчейну"
]
TITLE_PARTS3 = [
    "для стартапов", "для студентов", "для IT-специалистов", "для маркетологов",
    "для дизайнеров", "для HR-директоров", "для предпринимателей",
    "для госслужащих", "для некоммерческих организаций"
]

DESC_TEMPLATES = [
    "Участники научатся {}.",
    "Мероприятие посвящено {}.",
    "В программе: {}.",
    "Ключевые темы: {}.",
    "Мы обсудим {} и рассмотрим кейсы.",
    "Участники получат практические навыки по {}."
]
DESC_CONTENT = [
    "созданию нейросетей", "анализу больших данных", "защите от фишинга",
    "личному финансовому планированию", "устойчивому развитию городов",
    "созданию вирусного контента", "управлению agile-командами",
    "цифровизации бизнес-процессов", "разработке игр", "нейромаркетингу"
]

GOAL_TEMPLATES = [
    "Повышение квалификации в области {}.",
    "Обмен опытом между {}.",
    "Привлечение внимания к {}.",
    "Формирование сообщества {}.",
    "Выработка стратегии развития {}."
]
GOAL_CONTENT = [
    "искусственного интеллекта", "маркетинга", "экологии", "образования",
    "медицины", "культуры", "спорта", "инноваций", "социального предпринимательства"
]

SPEAKERS = [
    "Алексей Федотов (Яндекс)", "Мария Соколова (Сбер)", "Дмитрий Петров (Mail.ru)",
    "Анна Сидорова (Тинькофф)", "Игорь Ковалёв (Сколково)", "Елена Новикова (ВШЭ)",
    "Сергей Морозов (Росатом)", "Татьяна Григорьева (КРОС)", "Вадим Смирнов (МФТИ)",
    "Ольга Кузнецова (Авито)", "Павел Лебедев (VK)", "Ирина Волкова (Skillbox)",
    "Андрей Соколов (Mail.ru)", "Екатерина Ермакова (Яндекс.Практикум)",
    "Максим Орлов (Газпром нефть)", "Наталья Калинина (МГУ)"
]

AUDIENCES = [
    "студенты и молодые специалисты", "IT-специалисты с опытом от 3 лет",
    "маркетологи и PR-менеджеры", "дизайнеры и иллюстраторы",
    "руководители отделов продаж", "преподаватели и учёные",
    "предприниматели и стартаперы", "HR-директора и рекрутеры",
    "экологи и активисты", "широкая публика (12+)", "сотрудники госорганов"
]

ORGANIZERS = [
    "Кафедра ИИ Университета ИТМО", "Агентство инноваций Москвы", "Фонд «Сколково»",
    "Академия Яндекса", "Клуб «Стартап Сахалин»", "Музей современного искусства «Гараж»",
    "Эко-центр «Зелёная планета»", "Центр развития карьеры ВШЭ", "КРОС (Коммуникационная группа)",
    "Ассоциация выпускников МФТИ", "Технопарк «Калибр»", "Российское общество «Знание»"
]

def random_date(start_date=datetime(2025, 6, 1), end_date=datetime(2026, 12, 31)):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_time():
    return f"{random.randint(9, 19):02d}:{random.choice(['00','15','30','45'])}"

def random_phone():
    return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"

def maybe_empty(value, prob=0.15):
    return "" if random.random() < prob else value

def generate_title():
    t = random.choice(TITLE_TEMPLATES)
    if "{}" in t:
        if t.count("{}") == 1:
            return t.format(random.choice(TITLE_PARTS2).capitalize())
        elif t.count("{}") == 2:
            return t.format(random.choice(TITLE_PARTS1), random.choice(TITLE_PARTS2))
        else:
            return t.format(random.choice(TITLE_PARTS1), random.choice(TITLE_PARTS3))
    else:
        return t

def generate_description():
    template = random.choice(DESC_TEMPLATES)
    return template.format(random.choice(DESC_CONTENT))

def generate_goal():
    template = random.choice(GOAL_TEMPLATES)
    return template.format(random.choice(GOAL_CONTENT))

def generate_news_completion(plan):
    """Генерирует текст новости, используя только непустые поля, с разнообразными шаблонами."""
    title = plan.get("title", "")
    date = plan.get("date", "")
    time = plan.get("time", "")
    location = plan.get("location", "")
    format_type = plan.get("format_type", "")
    category = plan.get("category", "")
    participants = plan.get("participants_count", "")
    description = plan.get("description", "")
    goal = plan.get("goal", "")
    speaker = plan.get("speaker", "")
    audience = plan.get("audience", "")
    organizer = plan.get("organizer", "")
    end_time = plan.get("end_time", "")

    parts = []
    # Дата и время
    if date and time:
        parts.append(f"{date} в {time}")
    elif date:
        parts.append(f"{date}")
    elif time:
        parts.append(f"в {time}")
    # Место
    if location:
        if "Онлайн" in format_type:
            parts.append(f"в онлайн-формате из {location}")
        else:
            parts.append(f"в {location}")
    # Категория
    if category:
        parts.append(f"прошёл(ла) {category.lower()}")
    # Название
    if title:
        parts.append(f"«{title}»")
    else:
        parts.append("мероприятие")
    # Описание
    if description:
        # Убираем точку в конце, если есть
        desc_clean = description.rstrip('.').lower()
        parts.append(f". {desc_clean}")
    # Цель
    if goal:
        goal_clean = goal.rstrip('.').lower()
        parts.append(f" Цель – {goal_clean}.")
    # Спикеры
    if speaker:
        parts.append(f" Спикеры: {speaker}.")
    # Аудитория
    if audience:
        parts.append(f" Мероприятие ориентировано на {audience.lower()}.")
    # Организатор
    if organizer:
        parts.append(f" Организатор: {organizer}.")
    # Участники
    if participants and participants.isdigit():
        parts.append(f" Ожидается {participants} участников.")
    # Формат (если не очный)
    if format_type and format_type != "Очный":
        parts.append(f" Формат проведения – {format_type.lower()}.")
    # Время окончания
    if end_time and time:
        parts.append(f" Мероприятие продлится до {end_time}.")
    elif end_time and not time:
        parts.append(f" Окончание в {end_time}.")

    if not parts:
        return "Мероприятие состоится согласно плану."

    # Собираем строку, делаем первую букву заглавной
    result = " ".join(parts)
    result = result[0].upper() + result[1:]
    # Убираем лишние точки
    result = result.replace("..", ".").replace(". .", ". ").strip()
    # Если текст не заканчивается точкой, добавляем
    if result and result[-1] != '.':
        result += '.'
    return result

def create_advanced_dataset(num_examples=2000):
    dataset = []
    for i in range(num_examples):
        # Генерируем поля
        title = generate_title()
        event_date = random_date().strftime("%d.%m.%Y")
        start_time = random_time()
        end_time = f"{int(start_time[:2])+random.randint(1,3):02d}:{start_time[3:]}"
        location = random.choice(CITIES)
        format_type = random.choice(FORMATS)
        category = random.choice(CATEGORIES)
        participants_count = str(random.randint(10, 500))
        description = generate_description()
        goal = generate_goal()
        speaker = random.choice(SPEAKERS)
        audience = random.choice(AUDIENCES)
        organizer = random.choice(ORGANIZERS)

        # Случайно пропускаем поля (вероятность 10-30%)
        title = maybe_empty(title, 0.05)
        start_time = maybe_empty(start_time, 0.2)
        end_time = maybe_empty(end_time, 0.2)
        location = maybe_empty(location, 0.1)
        format_type = maybe_empty(format_type, 0.1)
        category = maybe_empty(category, 0.1)
        participants_count = maybe_empty(participants_count, 0.3)
        description = maybe_empty(description, 0.2)
        goal = maybe_empty(goal, 0.2)
        speaker = maybe_empty(speaker, 0.3)
        audience = maybe_empty(audience, 0.2)
        organizer = maybe_empty(organizer, 0.2)

        # Формируем промпт (только непустые поля)
        prompt_parts = []
        if title:
            prompt_parts.append(f"Название мероприятия: {title}")
        if event_date:
            prompt_parts.append(f"Дата: {event_date}")
        if start_time:
            prompt_parts.append(f"Время: {start_time}")
        if end_time:
            prompt_parts.append(f"Окончание: {end_time}")
        if location:
            prompt_parts.append(f"Место проведения: {location}")
        if format_type:
            prompt_parts.append(f"Формат: {format_type}")
        if category:
            prompt_parts.append(f"Категория: {category}")
        if participants_count:
            prompt_parts.append(f"Количество участников: {participants_count}")
        if description:
            prompt_parts.append(f"Описание: {description}")
        if goal:
            prompt_parts.append(f"Цель: {goal}")
        if speaker:
            prompt_parts.append(f"Спикер(ы): {speaker}")
        if audience:
            prompt_parts.append(f"Аудитория: {audience}")
        if organizer:
            prompt_parts.append(f"Организатор: {organizer}")

        prompt = ". ".join(prompt_parts) + ". Новость:"
        completion = generate_news_completion({
            "title": title,
            "date": event_date,
            "time": start_time,
            "end_time": end_time,
            "location": location,
            "format_type": format_type,
            "category": category,
            "participants_count": participants_count,
            "description": description,
            "goal": goal,
            "speaker": speaker,
            "audience": audience,
            "organizer": organizer,
            "id": i,
            "created_at": "",
            "updated_at": ""
        })

        dataset.append({"prompt": prompt, "completion": completion})
        if (i+1) % 500 == 0:
            print(f"Сгенерировано {i+1} примеров...")

    return dataset

if __name__ == "__main__":
    NUM = 2000  
    print(f"Генерация {NUM} примеров...")
    data = create_advanced_dataset(NUM)
    with open("advanced_dataset.jsonl", "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"✅ Датасет сохранён в advanced_dataset.jsonl. Всего примеров: {len(data)}")
    print("Пример первой записи:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2))