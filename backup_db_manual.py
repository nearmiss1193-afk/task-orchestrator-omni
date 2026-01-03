
import os
import json
import datetime
from supabase import create_client

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BACKUP_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\backups"

def backup_table(table_name, supabase):
    print(f"📦 Backing up {table_name}...")
    try:
        # Fetch all rows (limit 1000 for safety, loop for full if needed but simple for now)
        res = supabase.table(table_name).select("*").limit(2000).execute()
        data = res.data or []
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{table_name}_backup_{timestamp}.json"
        filepath = os.path.join(BACKUP_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
            
        print(f"✅ Saved {len(data)} rows to {filename}")
        return True
    except Exception as e:
        print(f"❌ Backup Failed for {table_name}: {e}")
        return False

def run_manual_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    if not SUPABASE_URL:
        print("⚠️ Supabase Credentials Missing. Skipping Data Backup.")
        return

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        backup_table("contacts_master", supabase)
        backup_table("brain_logs", supabase)
        backup_table("supervisor_logs", supabase)
    except Exception as e:
        print(f"Critical Backup Error: {e}")

if __name__ == "__main__":
    run_manual_backup()
