-- Таблица ролей
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица мероприятий (планов)
CREATE TABLE event_plans (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    event_time_end TIME,
    location VARCHAR(255),
    description TEXT,
    speaker VARCHAR(255),
    audience VARCHAR(100),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Таблица сгенерированных новостей
CREATE TABLE generated_news (
    id SERIAL PRIMARY KEY,
    event_plan_id INTEGER REFERENCES event_plans(id) ON DELETE CASCADE,
    generated_text TEXT NOT NULL,
    generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5)
);

-- Таблица логов генерации (для отслеживания работы нейросети)
CREATE TABLE generation_logs (
    id SERIAL PRIMARY KEY,
    event_plan_id INTEGER REFERENCES event_plans(id),
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt_text TEXT,
    generated_text TEXT,
    success BOOLEAN,
    error_message TEXT,
    inference_time_ms INTEGER
);

-- Таблица шаблонов для генерации новостей (разные стили)
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    template_text TEXT NOT NULL, -- шаблон с плейсхолдерами
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE
);

-- Таблица системных настроек
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP
);

-- Таблица отчётов (сформированные документы)
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50), -- 'docx', 'xlsx'
    file_path VARCHAR(500),
    generated_by INTEGER REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parameters JSONB -- параметры отчёта (даты, фильтры)
);

-- Таблица доступа к файлам (для требования доступа к ФС)
CREATE TABLE file_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    operation VARCHAR(50), -- 'READ', 'WRITE', 'DELETE'
    file_path VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица сессий пользователей (для безопасности)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем индексы для производительности
CREATE INDEX idx_event_plans_date ON event_plans(event_date);
CREATE INDEX idx_generated_news_approved ON generated_news(is_approved);
CREATE INDEX idx_generation_logs_timestamp ON generation_logs(timestamp);