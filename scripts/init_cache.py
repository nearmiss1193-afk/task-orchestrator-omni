
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
# Using the bit-perfect DATABASE_URL from deploy.py
DATABASE_URL = "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"

def init_cache_table():
    print("🐘 DATABASE: Initializing audit_cache table...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS audit_cache (
            url TEXT PRIMARY KEY,
            score INTEGER,
            raw_data JSONB,
            privacy_status TEXT,
            ai_status TEXT,
            last_audited_at TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        cur.execute(create_table_sql)
        conn.commit()
        print("✅ audit_cache table ready.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    init_cache_table()
