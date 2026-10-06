import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Таблицы в БД:")
for t in tables:
    print(f"  ✓ {t[0]}")

for table in ['users', 'quizzes', 'attempts']:
    print(f"\nСтруктура таблицы {table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    for col in cursor.fetchall():
        col_id, name, col_type, notnull, default, pk = col
        key = "PK" if pk else ""
        print(f"  - {name} ({col_type}) {key}")

conn.close()