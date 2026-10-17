import sqlite3
conn = sqlite3.connect('c:/Users/HP/OneDrive/Desktop/warehouse_ai_v3/warehouse.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE message ADD COLUMN attachment VARCHAR(255) DEFAULT ''")
    conn.commit()
    print("Success")
except Exception as e:
    print("Error:", e)
conn.close()
