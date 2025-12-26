import sqlite3
DB_PATH = "ai_accounts.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM conversations")
print(f"Total conversations: {cursor.fetchone()[0]}")
cursor.execute("SELECT title, created_at FROM conversations LIMIT 20")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
