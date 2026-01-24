
import os
from supabase import create_client
from dotenv import load_dotenv
import datetime

load_dotenv('.env.local')

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("🔍 DIAGNOSTIC REPORT")
print("-------------------")

# 1. Lead Counts by Status
try:
    print("\n📊 Lead Counts:")
    # Fetch all statuses (inefficient for millions, fine for hundreds)
    res = supabase.table("contacts_master").select("status").execute()
    counts = {}
    for row in res.data:
        s = row.get('status', 'unknown') or 'unknown'
        counts[s] = counts.get(s, 0) + 1
    
    for s, c in counts.items():
        print(f"  - {s}: {c}")
except Exception as e:
    print(f"❌ Error counting leads: {e}")

# 2. Recent Brain Logs
try:
    print("\n📜 Recent Logs (Last 10):")
    res = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(10).execute()
    for log in res.data:
        print(f"  [{log['timestamp']}] {log['message']}")
except Exception as e:
    print(f"❌ Error fetching logs: {e}")
