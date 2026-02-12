"""Full system audit — query all critical Supabase tables"""
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("=" * 60)
print("FULL SYSTEM AUDIT")
print("=" * 60)

# 1. Last outreach
print("\n[1] LAST 5 OUTREACH (outbound_touches)")
try:
    r = sb.table("outbound_touches").select("id,ts,channel,status").order("ts", desc=True).limit(5).execute()
    if r.data:
        for x in r.data:
            print(f"    {x.get('ts','')} | {x.get('channel','')} | {x.get('status','')}")
    else:
        print("    NONE - Zero outreach records")
except Exception as e:
    print(f"    ERROR: {e}")

# 2. Heartbeat
print("\n[2] LAST 5 HEARTBEATS (system_health_log)")
try:
    r = sb.table("system_health_log").select("checked_at,status,details").order("checked_at", desc=True).limit(5).execute()
    if r.data:
        for x in r.data:
            print(f"    {x.get('checked_at','')} | {x.get('status','')}")
    else:
        print("    NONE - No heartbeat records")
except Exception as e:
    print(f"    ERROR: {e}")

# 3. Campaign mode
print("\n[3] CAMPAIGN MODE (system_state)")
try:
    r = sb.table("system_state").select("key,status").eq("key", "campaign_mode").execute()
    if r.data:
        print(f"    campaign_mode = {r.data[0].get('status','')}")
    else:
        print("    NOT SET")
except Exception as e:
    print(f"    ERROR: {e}")

# 4. Lead counts
print("\n[4] LEADS BY STATUS (contacts_master)")
try:
    r = sb.rpc("", {}).execute()
except:
    pass
try:
    statuses = ["new", "research_done", "contacted", "replied", "customer", "sequence_complete"]
    for s in statuses:
        r = sb.table("contacts_master").select("id", count="exact").eq("status", s).limit(1).execute()
        print(f"    {s}: {r.count}")
except Exception as e:
    print(f"    ERROR: {e}")

# 5. Total leads
print("\n[5] TOTAL LEADS")
try:
    r = sb.table("contacts_master").select("id", count="exact").limit(1).execute()
    print(f"    Total contacts: {r.count}")
except Exception as e:
    print(f"    ERROR: {e}")

# 6. Leads with contact info
print("\n[6] LEADS WITH CONTACT INFO (contactable)")
try:
    r = sb.table("contacts_master").select("id,email,phone", count="exact").neq("email", "").limit(1).execute()
    print(f"    Has email: {r.count}")
    r2 = sb.table("contacts_master").select("id,phone", count="exact").neq("phone", "").limit(1).execute()
    print(f"    Has phone: {r2.count}")
except Exception as e:
    print(f"    ERROR: {e}")

# 7. Outreach count last 30 min
print("\n[7] OUTREACH LAST 30 MINUTES (THE TRUTH TEST)")
try:
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    r = sb.table("outbound_touches").select("id", count="exact").gte("ts", cutoff).limit(1).execute()
    print(f"    Count: {r.count}")
    if r.count and r.count > 0:
        print("    VERDICT: OUTREACH IS ACTIVE")
    else:
        print("    VERDICT: NO RECENT OUTREACH")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
