
import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def run_migration():
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase connection failed.")
        return

    print("🔧 Running Migration: Add 'campaign_mode' to 'system_state'...")
    sql = "ALTER TABLE system_state ADD COLUMN IF NOT EXISTS campaign_mode text DEFAULT 'normal';"
    
    try:
        # Attempt via rpc(exec_sql) - standard pattern in this repo
        res = supabase.rpc("exec_sql", {"query": sql}).execute()
        print(f"✅ Migration Result: {res}")
    except Exception as e:
        print(f"❌ Migration Failed with Exception: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    run_migration()
