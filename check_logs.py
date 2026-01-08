import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def check_logs():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM public.system_logs ORDER BY created_at DESC LIMIT 5;")
        logs = cur.fetchall()
        
        print(f"✅ Found {len(logs)} logs.")
        for log in logs:
            print(f"   [{log[2]}] {log[3]} (Worker: {log[1]})")
        
        conn.close()
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")

if __name__ == "__main__":
    check_logs()
