
import os
import datetime
from supabase import create_client
from dotenv import load_dotenv

import sys
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

# Setup Supabase
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

print("--- 📊 EMPIRE SYSTEM STATUS CHECK ---")
print(f"Time: {datetime.datetime.now().isoformat()}")

# 1. Check Contacts Status Distribution
try:
    res = supabase.table("contacts_master").select("status").execute()
    statuses = {}
    for row in res.data:
        s = row.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1
    
    print("\n[Contacts Pipeline Status]")
    for s, c in statuses.items():
        print(f"  - {s}: {c}")

except Exception as e:
    print(f"Error fetching contacts: {e}")

# 2. Check Recent Activity (Last 1 Hour)
try:
    one_hour_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat()
    
    # Check for recent outreach/research
    # Note: 'updated_at' column might not exist or be reliable, checking 'last_outreach_at' if available, otherwise checking 'created_at' of related logs if possible.
    # checking brain_logs if table exists
    
    logs = supabase.table("brain_logs").select("*").gt("timestamp", one_hour_ago).order("timestamp", desc=True).limit(10).execute()
    
    print(f"\n[Recent Brain Logs (Last 1h)] - Found {len(logs.data)}")
    for log in logs.data:
        print(f"  [{log['timestamp']}] {log.get('message', '')[:80]}...")

except Exception as e:
    # Brain logs might not exist yet if not fully set up or permissions issue
    print(f"\n[Logs] Could not fetch recent logs or table empty: {e}")

# 3. Check for recent 'nurture_queue' or 'research_done' updates (approximate)
# We can't easily query "updated_at" unless we added that column.
# But we can check if any contacts have 'last_outreach_at' in the last hour.

try:
    recent_outreach = supabase.table("contacts_master").select("full_name, status, last_outreach_at").gt("last_outreach_at", one_hour_ago).execute()
    print(f"\n[Recent Outreach/Activity (Last 1h)] - Found {len(recent_outreach.data)}")
    for c in recent_outreach.data:
        print(f"  - {c.get('full_name')}: {c.get('status')} ({c.get('last_outreach_at')})")

except Exception as e:
    print(f"Error checking recent outreach: {e}")

