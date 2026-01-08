import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def verify_table():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT to_regclass('public.call_transcripts');")
        exists = cur.fetchone()[0]
        print(f"VERIFY: Table 'public.call_transcripts' exists? {exists}")
        
        if exists:
             cur.execute("SELECT count(*) FROM public.call_transcripts;")
             count = cur.fetchone()[0]
             print(f"Data Count: {count} rows")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_table()
