import os
from dotenv import load_dotenv
from modules.database.supabase_client import get_supabase

def run_migration():
    load_dotenv()
    sb = get_supabase()
    with open('sql/social_logs_migration.sql', 'r') as f:
        sql = f.read()
    
    print("🚀 Applying social_logs migration...")
    try:
        # Assuming the exec_sql RPC exists as seen in other scripts
        sb.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Migration applied successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
