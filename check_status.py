import sys; sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone, timedelta

sb = get_supabase()
now = datetime.now(timezone.utc)

# Prospector status
r = sb.table("system_state").select("*").eq("key", "prospector_last_run").execute()
print("=== PROSPECTOR STATUS ===")
if r.data:
    row = r.data[0]
    print(f"  Status: {row.get('status')}")
    print(f"  Last error/timestamp: {row.get('last_error')}")

r2 = sb.table("system_state").select("*").eq("key", "last_prospect_half_hour").execute()
if r2.data:
    print(f"  Last half-hour key: {r2.data[0].get('status')}")

# Heartbeat check
r3 = sb.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(3).execute()
print("\n=== RECENT HEARTBEATS ===")
for h in r3.data:
    ts = datetime.fromisoformat(h["checked_at"].replace("Z","+00:00"))
    age = int((now - ts).total_seconds() / 60)
    print(f"  {h['checked_at']} | {h['status']} | {age} min ago")

# Count leads created in last 12 hours
cutoff = (now - timedelta(hours=12)).isoformat()
r4 = sb.table("contacts_master").select("id", count="exact").gte("created_at", cutoff).execute()
new_12h = r4.count if r4.count else len(r4.data)
print(f"\n=== NEW LEADS (last 12h) ===")
print(f"  {new_12h} leads added since {cutoff[:16]}")

# Total lead count
r5 = sb.table("contacts_master").select("id", count="exact").execute()
total = r5.count if r5.count else len(r5.data)
print(f"  Total leads now: {total}")

# Check for any Mountain/West Coast leads
r6 = sb.table("contacts_master").select("lead_source").like("lead_source", "%mountain%").execute()
r7 = sb.table("contacts_master").select("lead_source").like("lead_source", "%west_coast%").execute()
print(f"\n=== REGIONAL BREAKDOWN ===")
print(f"  Mountain leads: {len(r6.data)}")
print(f"  West Coast leads: {len(r7.data)}")
print(f"  Florida (everything else): {total - len(r6.data) - len(r7.data)}")
