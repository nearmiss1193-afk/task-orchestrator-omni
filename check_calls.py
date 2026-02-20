"""Diagnose prospecting status and recent activity"""
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
sb = get_supabase()

# 1. Check prospector_last_run
print("=== PROSPECTOR STATUS ===")
try:
    p = sb.table("system_state").select("*").eq("key", "prospector_last_run").execute()
    if p.data:
        print(f"  Last run: {p.data[0].get('status', '?')}")
    else:
        print("  No prospector_last_run record found!")
except Exception as e:
    print(f"  Error: {e}")

# 2. Check campaign_mode
print("\n=== CAMPAIGN MODE ===")
try:
    c = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
    if c.data:
        print(f"  Mode: {c.data[0].get('status', '?')}")
    else:
        print("  No campaign_mode record!")
except Exception as e:
    print(f"  Error: {e}")

# 3. Recent outbound activity
print("\n=== RECENT OUTREACH (last 24h) ===")
try:
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    touches = sb.table("outbound_touches").select("channel,status,company,phone,ts").gte("ts", cutoff).order("ts", desc=True).limit(10).execute()
    if touches.data:
        for t in touches.data:
            print(f"  {t.get('ts','?')[:16]} | {t.get('channel','?'):5} | {t.get('status','?'):10} | {t.get('company','?')[:25]} | {t.get('phone','?')}")
    else:
        print("  No outreach in last 24h!")
except Exception as e:
    print(f"  Error: {e}")

# 4. Lead pool
print("\n=== LEAD POOL ===")
try:
    for status in ['new', 'research_done', 'email_sent', 'calling_initiated', 'contacted']:
        ct = sb.table("contacts_master").select("id", count="exact").eq("status", status).execute()
        count = ct.count if ct.count is not None else len(ct.data)
        if count > 0:
            print(f"  {status}: {count}")
except Exception as e:
    print(f"  Error: {e}")

# 5. Check recent heartbeats
print("\n=== HEARTBEATS (last 3) ===")
try:
    hb = sb.table("system_health_log").select("checked_at,status,details").order("checked_at", desc=True).limit(3).execute()
    for h in hb.data:
        ts = h.get('checked_at','?')[:19]
        status = h.get('status','?')
        details = h.get('details', {})
        print(f"  {ts} | {status} | {details}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone.")
