"""
CRITICAL: Campaign Outreach Diagnosis
Why isn't anything going out? Let's find out.
"""
import os, sys, json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

results = {}

# 1. Campaign mode
camp = supabase.table("system_state").select("status").eq("key", "campaign_mode").execute()
results["campaign_mode"] = camp.data[0].get("status") if camp.data else "MISSING"

# 2. Outreach in last 1 hour
cutoff_1h = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
r1h = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_1h).execute()
results["outreach_1h"] = r1h.count if r1h.count is not None else 0

# 3. Outreach in last 6 hours
cutoff_6h = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
r6h = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_6h).execute()
results["outreach_6h"] = r6h.count if r6h.count is not None else 0

# 4. Outreach in last 24 hours
cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
r24h = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_24h).execute()
results["outreach_24h"] = r24h.count if r24h.count is not None else 0

# 5. Last outreach timestamp
last = supabase.table("outbound_touches").select("ts,channel,company").order("ts", desc=True).limit(3).execute()
results["last_3_touches"] = last.data if last.data else []

# 6. Heartbeat - last 30 min
cutoff_30m = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
hb = supabase.table("system_health_log").select("checked_at,status", count="exact").gte("checked_at", cutoff_30m).execute()
results["heartbeats_30m"] = hb.count if hb.count is not None else 0

# 7. Lead pool by status
statuses = supabase.table("contacts_master").select("status").execute()
status_counts = {}
for row in (statuses.data or []):
    s = row.get("status", "unknown")
    status_counts[s] = status_counts.get(s, 0) + 1
results["lead_status_breakdown"] = dict(sorted(status_counts.items(), key=lambda x: -x[1]))

# 8. Fresh leads available (new + research_done)
fresh = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
results["fresh_leads"] = fresh.count if fresh.count is not None else 0

# 9. Check if orchestrator ran recently
orch = supabase.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
results["last_heartbeat"] = orch.data[0].get("checked_at") if orch.data else "NONE"

with open("campaign_diagnosis.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("Diagnosis written to campaign_diagnosis.json")
