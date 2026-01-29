import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, phone, email, status FROM contacts_master LIMIT 5;")
    leads = cur.fetchall()
    for lead in leads:
        print(f"ID: {lead[0]} | Name: {lead[1]} | Phone: {lead[2]} | Email: {lead[3]} | Status: {lead[4]}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
