import sqlite3
conn = sqlite3.connect('c:/Users/HP/OneDrive/Desktop/warehouse_ai_v3/warehouse.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE movement ADD COLUMN verified_by VARCHAR(50) DEFAULT ''")
    cursor.execute("ALTER TABLE issue ADD COLUMN resolved_by VARCHAR(50) DEFAULT ''")
    conn.commit()
    print("Success")
except Exception as e:
    print("Error:", e)
conn.close()
