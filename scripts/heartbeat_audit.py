import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.getcwd())

try:
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    print("💓 Querying System Heartbeats (Last 10 Days)...")
    res = supabase.table("system_health_log").select("checked_at, status, details").order("checked_at", desc=True).limit(20).execute()
    
    if not res.data:
        print("📭 No heartbeats found in log.")
    else:
        for row in res.data:
            print(f"- {row['checked_at']} | {row['status']} | {row['details']}")

except Exception as e:
    print(f"❌ Error: {e}")
