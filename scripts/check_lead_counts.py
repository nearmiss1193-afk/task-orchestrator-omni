import os, psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_leads():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT status, count(*) FROM public.contacts_master GROUP BY status")
        counts = dict(cur.fetchall())
        print(counts)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_leads()
