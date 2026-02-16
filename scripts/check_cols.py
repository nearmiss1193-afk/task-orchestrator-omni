import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_columns():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'contacts_master'")
        cols = [r[0] for r in cur.fetchall()]
        print(f"COLUMNS: {cols}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_columns()
