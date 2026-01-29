import os
import psycopg2
from dotenv import load_dotenv

def get_ghl_id():
    load_dotenv(".env")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT ghl_id FROM contacts_master WHERE id = 'c086f2ce-72f5-4f9f-b414-e0432908c6bc'")
    res = cur.fetchone()
    if res:
        print(res[0])
    else:
        print("Lead not found")
    conn.close()

if __name__ == "__main__":
    get_ghl_id()
