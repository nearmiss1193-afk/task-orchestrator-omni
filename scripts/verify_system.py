
import os
import sys
from supabase import create_client

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # Try to load from .env.local if not in env
    try:
        with open("modules/orchestrator/dashboard/.env.local", "r") as f:
            for line in f:
                if "NEXT_PUBLIC_SUPABASE_URL" in line:
                    SUPABASE_URL = line.split("=")[1].strip().strip('"')
                if "NEXT_PUBLIC_SUPABASE_ANON_KEY" in line:
                    SUPABASE_KEY = line.split("=")[1].strip().strip('"')
    except:
        pass

if not SUPABASE_URL:
    print("❌ ERROR: Could not find Supabase credentials.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n--- 🛡️ EMPIRE SYSTEM AUDIT 🛡️ ---\n")

# 1. Check Contacts
try:
    res = supabase.table("contacts_master").select("*", count="exact", head=True).execute()
    print(f"✅ Leads Database: {res.count} records")
except Exception as e:
    print(f"❌ Database Error: {e}")

# 2. Check Logs (Tasks Completed)
print("\n--- 📜 RECENT ACTIVITY LOGS ---")
try:
    logs = supabase.table("brain_logs").select("timestamp, message").order("timestamp", desc=True).limit(5).execute()
    if logs.data:
        for log in logs.data:
            print(f"[{log['timestamp']}] {log['message']}")
    else:
        print("⚠️ No logs found yet (System may be warming up).")
except Exception as e:
    print(f"❌ Log Error: {e}")

print("\n--- 🏁 AUDIT COMPLETE ---")
