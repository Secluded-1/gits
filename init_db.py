"""
Скрипт инициализации базы данных проекта
«Генератор интерактивных обучающих тренажёров».

Запуск: python init_db.py
Результат: файл app.db с тремя таблицами.
"""

import sqlite3

# Подключение к БД (файл создастся автоматически)
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Включаем поддержку внешних ключей (по умолчанию в SQLite отключены)
cursor.execute("PRAGMA foreign_keys = ON;")

# --- Таблица users (преподаватели) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# --- Таблица quizzes (созданные тренажёры) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS quizzes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    title          TEXT,
    source_text    TEXT,
    quiz_type      TEXT,
    difficulty     TEXT,
    questions_json TEXT,
    public_slug    TEXT    UNIQUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# --- Таблица attempts (попытки прохождения) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS attempts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id       INTEGER NOT NULL,
    student_name  TEXT,
    score         INTEGER,
    total         INTEGER,
    answers_json  TEXT,
    duration_sec  INTEGER,
    completed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);
""")

conn.commit()
conn.close()

print("✅ База данных создана: app.db")
print("   Таблицы: users, quizzes, attempts")