import sqlite3

conn = sqlite3.connect('c:/Users/HP/OneDrive/Desktop/warehouse_ai_v3/warehouse.db')
cursor = conn.cursor()

try:
    cursor.execute('''
    CREATE TABLE issue_comment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_id INTEGER NOT NULL,
        sender_id VARCHAR(50) NOT NULL,
        body TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    print("Success: issue_comment table created")
except Exception as e:
    print("Error:", e)

conn.close()
