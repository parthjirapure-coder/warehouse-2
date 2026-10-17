import sqlite3

conn = sqlite3.connect('c:/Users/HP/OneDrive/Desktop/warehouse_ai_v3/warehouse.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE message ADD COLUMN deleted_by_sender BOOLEAN DEFAULT 0")
    cursor.execute("ALTER TABLE message ADD COLUMN deleted_by_receiver BOOLEAN DEFAULT 0")
    conn.commit()
    print("Columns added successfully.")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
