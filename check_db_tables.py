
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def list_tables():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        
        print(f"📊 Found {len(tables)} tables in DB:")
        for t in tables:
            print(f" - {t[0]}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error listing tables: {e}")

if __name__ == "__main__":
    list_tables()
