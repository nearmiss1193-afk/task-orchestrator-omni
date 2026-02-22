import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'contacts_master';")
columns = cur.fetchall()
for col in columns:
    print(f"{col[0]}: {col[1]}")
