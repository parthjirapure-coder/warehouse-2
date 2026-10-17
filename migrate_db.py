import sqlite3
from pathlib import Path

def run_migrations():
    db_path = Path(__file__).resolve().parent / 'warehouse.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE issue ADD COLUMN photo VARCHAR(255) DEFAULT ''")
        conn.commit()
        print("Migration applied: Added 'photo' column to 'issue' table.")
    except Exception as e:
        if "duplicate column name" in str(e):
            print("Migration already applied: 'photo' column exists.")
        else:
            print("Migration error:", e)
    finally:
        conn.close()

