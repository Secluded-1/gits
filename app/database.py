"""
Модуль подключения к базе данных SQLite.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "app.db"


def get_db():
    """Генератор подключений к БД для FastAPI Depends."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()