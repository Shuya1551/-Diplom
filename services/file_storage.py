"""
Хранение данных в CSV-файлах (вместо PostgreSQL).
"""

import csv
import os
import bcrypt
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
PLANS_FILE = os.path.join(DATA_DIR, "event_plans.csv")
NEWS_FILE = os.path.join(DATA_DIR, "generated_news.csv")
LOGS_FILE = os.path.join(DATA_DIR, "generation_logs.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.csv")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def read_csv(filepath, fieldnames):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(filepath, fieldnames, rows):
    ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def get_next_id(filepath, id_field="id"):
    rows = read_csv(filepath, [])
    if not rows:
        return 1
    return max(int(row[id_field]) for row in rows) + 1

# ---------- ПОЛЬЗОВАТЕЛИ ----------
USER_FIELDS = ["id", "username", "password_hash", "email", "is_admin", "created_at", "last_login"]

def init_admin_user():
    users = get_all_users()
    if not users:
        admin_pass = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        create_user("admin", admin_pass, "admin@example.com", is_admin=True)

def get_all_users() -> List[Dict]:
    return read_csv(USERS_FILE, USER_FIELDS)

def get_user_by_id(user_id: int) -> Optional[Dict]:
    for u in get_all_users():
        if int(u["id"]) == user_id:
            return u
    return None

def get_user_by_username(username: str) -> Optional[Dict]:
    for u in get_all_users():
        if u["username"] == username:
            return u
    return None

def get_user_by_email(email: str) -> Optional[Dict]:
    for u in get_all_users():
        if u["email"] == email:
            return u
    return None

def authenticate_user(login: str, password: str) -> Optional[Dict]:
    user = get_user_by_username(login) or get_user_by_email(login)
    if not user:
        return None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        user["last_login"] = datetime.now().isoformat()
        users = get_all_users()
        for i, u in enumerate(users):
            if u["id"] == user["id"]:
                users[i] = user
                break
        write_csv(USERS_FILE, USER_FIELDS, users)
        return {
            "id": int(user["id"]),
            "username": user["username"],
            "role": "admin" if user["is_admin"] == "True" else "user"
        }
    return None

def create_user(username: str, password_hash: str, email: str, is_admin: bool = False) -> Optional[int]:
    if get_user_by_username(username) or get_user_by_email(email):
        return None
    new_id = get_next_id(USERS_FILE)
    users = get_all_users()
    users.append({
        "id": str(new_id),
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "is_admin": str(is_admin),
        "created_at": datetime.now().isoformat(),
        "last_login": ""
    })
    write_csv(USERS_FILE, USER_FIELDS, users)
    return new_id

def update_user(user_id: int, email: str = None, role_id: int = None):
    users = get_all_users()
    for u in users:
        if int(u["id"]) == user_id:
            if email is not None:
                u["email"] = email
            if role_id is not None:
                u["is_admin"] = "True" if role_id == 1 else "False"
            break
    write_csv(USERS_FILE, USER_FIELDS, users)
    return True

def delete_user(user_id: int) -> bool:
    users = get_all_users()
    new_users = [u for u in users if int(u["id"]) != user_id]
    if len(new_users) == len(users):
        return False
    write_csv(USERS_FILE, USER_FIELDS, new_users)
    return True

def change_password(user_id: int, new_hash: str) -> bool:
    users = get_all_users()
    for u in users:
        if int(u["id"]) == user_id:
            u["password_hash"] = new_hash
            break
    write_csv(USERS_FILE, USER_FIELDS, users)
    return True

def get_roles():
    return [(1, "admin"), (2, "user")]

def get_role_id_by_name(name: str):
    return 1 if name == "admin" else 2

# ---------- ПЛАНЫ ----------
PLAN_FIELDS = ["id", "title", "event_date", "event_time", "event_end_time", "location",
               "description", "speaker", "audience", "category", "created_by", "created_at", "updated_at",
               "participants_count", "goal", "organizer", "format_type"]

def get_all_event_plans(user_id=None, user_role=None):
    plans = read_csv(PLANS_FILE, PLAN_FIELDS)
    if user_role == "admin":
        return plans
    if user_id is not None:
        return [p for p in plans if int(p.get("created_by", 0)) == user_id]
    return plans

def get_event_plan_by_id(plan_id, user_id=None, user_role=None):
    plans = get_all_event_plans(user_id, user_role)
    for p in plans:
        if int(p["id"]) == plan_id:
            return p
    return None

def create_event_plan(title, event_date, event_time, event_end_time, location,
                      description, speaker, audience, category, created_by,
                      participants_count=0, goal="", organizer="", format_type=""):
    new_id = get_next_id(PLANS_FILE)
    plans = get_all_event_plans()
    plans.append({
        "id": str(new_id),
        "title": title,
        "event_date": event_date.isoformat() if event_date else "",
        "event_time": event_time or "",
        "event_end_time": event_end_time or "",
        "location": location or "",
        "description": description or "",
        "speaker": speaker or "",
        "audience": audience or "",
        "category": category or "",
        "created_by": str(created_by),
        "created_at": datetime.now().isoformat(),
        "updated_at": "",
        "participants_count": str(participants_count),
        "goal": goal or "",
        "organizer": organizer or "",
        "format_type": format_type or ""
    })
    write_csv(PLANS_FILE, PLAN_FIELDS, plans)
    return new_id

def update_event_plan(plan_id, title, event_date, event_time, event_end_time,
                      location, description, speaker, audience, category,
                      participants_count=None, goal=None, organizer=None, format_type=None):
    plans = get_all_event_plans()
    for p in plans:
        if int(p["id"]) == plan_id:
            p.update({
                "title": title,
                "event_date": event_date.isoformat() if event_date else "",
                "event_time": event_time or "",
                "event_end_time": event_end_time or "",
                "location": location or "",
                "description": description or "",
                "speaker": speaker or "",
                "audience": audience or "",
                "category": category or "",
                "updated_at": datetime.now().isoformat()
            })
            if participants_count is not None:
                p["participants_count"] = str(participants_count)
            if goal is not None:
                p["goal"] = goal
            if organizer is not None:
                p["organizer"] = organizer
            if format_type is not None:
                p["format_type"] = format_type
            break
    write_csv(PLANS_FILE, PLAN_FIELDS, plans)
    return True

def delete_event_plan(plan_id):
    plans = get_all_event_plans()
    new_plans = [p for p in plans if int(p["id"]) != plan_id]
    write_csv(PLANS_FILE, PLAN_FIELDS, new_plans)
    return True

# ---------- НОВОСТИ ----------
NEWS_FIELDS = ["id", "event_plan_id", "generated_text", "generation_date", "is_approved", "approved_by", "rating", "user_id"]

def save_generated_news(event_plan_id, generated_text, user_id, rating=None):
    new_id = get_next_id(NEWS_FILE)
    news = get_all_generated_news()
    news.append({
        "id": str(new_id),
        "event_plan_id": str(event_plan_id),
        "generated_text": generated_text,
        "generation_date": datetime.now().isoformat(),
        "is_approved": "False",
        "approved_by": str(user_id),
        "rating": str(rating) if rating is not None else "",
        "user_id": str(user_id)
    })
    write_csv(NEWS_FILE, NEWS_FIELDS, news)
    return new_id

def get_all_generated_news(user_id=None, user_role=None):
    news = read_csv(NEWS_FILE, NEWS_FIELDS)
    if user_role == "admin":
        return news
    if user_id is not None:
        return [n for n in news if int(n.get("user_id", 0)) == user_id]
    return news

def get_news_by_plan_id(event_plan_id, user_id=None, user_role=None):
    news = get_all_generated_news(user_id, user_role)
    return [n for n in news if int(n["event_plan_id"]) == event_plan_id]

def get_news_by_id(news_id):
    for n in get_all_generated_news():
        if int(n["id"]) == news_id:
            return n
    return None

def get_news_by_user_id(user_id):
    news = get_all_generated_news()
    result = []
    for n in news:
        if int(n.get("user_id", 0)) == user_id:
            plan = get_event_plan_by_id(int(n["event_plan_id"]))
            result.append((
                int(n["id"]),
                n["generated_text"],
                n["generation_date"],
                n["is_approved"] == "True",
                int(n["rating"]) if n["rating"] else None,
                plan["title"] if plan else "Неизвестный план"
            ))
    return result

def get_recent_news(limit=5, user_id=None, user_role=None):
    news = get_all_generated_news(user_id, user_role)
    news.sort(key=lambda x: x["generation_date"], reverse=True)
    recent = []
    for n in news[:limit]:
        plan = get_event_plan_by_id(int(n["event_plan_id"]))
        recent.append((
            int(n["id"]),
            n["generated_text"],
            n["generation_date"][:10],
            plan["title"] if plan else "Неизвестный план"
        ))
    return recent

def update_generated_news(news_id, new_text):
    """Обновляет текст сгенерированной новости."""
    news_list = get_all_generated_news()
    for item in news_list:
        if int(item["id"]) == news_id:
            item["generated_text"] = new_text
            break
    else:
        return False
    write_csv(NEWS_FILE, NEWS_FIELDS, news_list)
    return True

def delete_generated_news(news_id):
    news = get_all_generated_news()
    new_news = [n for n in news if int(n["id"]) != news_id]
    write_csv(NEWS_FILE, NEWS_FIELDS, new_news)
    return True

# ---------- ЛОГИ ----------
LOG_FIELDS = ["id", "event_plan_id", "user_id", "timestamp", "prompt_text", "generated_text", "success", "error_message", "inference_time_ms"]

def log_generation(event_plan_id, user_id, prompt_text, generated_text, success, error_message=None, inference_time_ms=None):
    new_id = get_next_id(LOGS_FILE)
    logs = read_csv(LOGS_FILE, LOG_FIELDS)
    logs.append({
        "id": str(new_id),
        "event_plan_id": str(event_plan_id) if event_plan_id else "",
        "user_id": str(user_id),
        "timestamp": datetime.now().isoformat(),
        "prompt_text": prompt_text,
        "generated_text": generated_text,
        "success": str(success),
        "error_message": error_message or "",
        "inference_time_ms": str(inference_time_ms) if inference_time_ms else ""
    })
    write_csv(LOGS_FILE, LOG_FIELDS, logs)

def get_all_generation_logs(limit=100):
    logs = read_csv(LOGS_FILE, LOG_FIELDS)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    result = []
    for log in logs[:limit]:
        user = get_user_by_id(int(log["user_id"]))
        plan = get_event_plan_by_id(int(log["event_plan_id"])) if log["event_plan_id"] else None
        result.append((
            int(log["id"]),
            log["timestamp"],
            user["username"] if user else "неизвестно",
            plan["title"] if plan else "-",
            log["success"] == "True",
            int(log["inference_time_ms"]) if log["inference_time_ms"] else 0,
            log["error_message"]
        ))
    return result

def get_generation_stats():
    logs = read_csv(LOGS_FILE, LOG_FIELDS)
    total = len(logs)
    successful = sum(1 for l in logs if l["success"] == "True")
    times = [int(l["inference_time_ms"]) for l in logs if l["inference_time_ms"] and l["success"] == "True"]
    avg_time = sum(times) / len(times) if times else 0
    return {"total": total, "successful": successful, "avg_time_ms": avg_time}

# ---------- НАСТРОЙКИ ----------
SETTINGS_FIELDS = ["key", "value", "updated_by", "updated_at"]

def get_setting(key, default=None):
    for s in read_csv(SETTINGS_FILE, SETTINGS_FIELDS):
        if s["key"] == key:
            return s["value"]
    return default

def set_setting(key, value, updated_by=None):
    settings = read_csv(SETTINGS_FILE, SETTINGS_FIELDS)
    found = False
    for s in settings:
        if s["key"] == key:
            s["value"] = value
            s["updated_by"] = str(updated_by) if updated_by else ""
            s["updated_at"] = datetime.now().isoformat()
            found = True
            break
    if not found:
        settings.append({
            "key": key,
            "value": value,
            "updated_by": str(updated_by) if updated_by else "",
            "updated_at": datetime.now().isoformat()
        })
    write_csv(SETTINGS_FILE, SETTINGS_FIELDS, settings)

def get_all_settings():
    return {s["key"]: s["value"] for s in read_csv(SETTINGS_FILE, SETTINGS_FIELDS)}