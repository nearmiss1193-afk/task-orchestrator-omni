
import os
import sys
import datetime
import traceback
from dotenv import load_dotenv
from supabase import create_client

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('.env.local')

def run_check():
    try:
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ MISSING CREDENTIALS")
            return

        supabase = create_client(url, key)
        print(f"✅ Connected to {url}")

        # 1. Count Contacts
        print("\n--- CONTACTS ---")
        res = supabase.table("contacts_master").select("status", count="exact").execute()
        # Group by status
        counts = {}
        for row in res.data:
            s = row.get('status', 'unknown')
            counts[s] = counts.get(s, 0) + 1
        
        for k, v in counts.items():
            print(f"  {k}: {v}")
            
        # 2. Latest Logs
        print("\n--- RECENT LOGS (Last 5) ---")
        logs = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(5).execute()
        for log in logs.data:
            print(f"  [{log['timestamp']}] {log.get('message', '')}")
            
    except Exception:
        print("❌ CRITICAL FAILURE")
        traceback.print_exc()

if __name__ == "__main__":
    run_check()
