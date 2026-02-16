
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"

def update_schema():
    print("🐘 DATABASE: Standardizing outbound_touches schema...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Add 'opened' column if not exists
        cur.execute("""
            ALTER TABLE outbound_touches 
            ADD COLUMN IF NOT EXISTS opened BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS opened_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
        """)
        
        conn.commit()
        print("✅ outbound_touches schema standardized.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    update_schema()
