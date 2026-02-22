import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS onboarding_status JSONB DEFAULT '{}'::jsonb;")
    print("✅ Added onboarding_status column to contacts_master.")
except Exception as e:
    print(f"❌ Error modifying database: {e}")
