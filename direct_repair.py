import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
# Hande URL-encoded @ in password and try pooler port 6543
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('%40', '@').replace(':5432/', ':6543/')

sql_statements = [
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS city TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS state TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS industry TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS website TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_called TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_contact_at TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS agent_research JSONB DEFAULT '{}'::jsonb;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS personalized_copy TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;"
]

def run_migration():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return

    print("🚀 Connecting to PostgreSQL directly...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        for sql in sql_statements:
            try:
                cur.execute(sql)
                print(f"✅ Executed: {sql[:40]}...")
            except Exception as e:
                print(f"⚠️ Warning: {sql[:40]}... Error: {e}")
        
        cur.close()
        conn.close()
        print("🏁 Migration Complete.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    run_migration()
