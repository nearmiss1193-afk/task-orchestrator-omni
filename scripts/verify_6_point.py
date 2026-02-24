import os
import sys
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Step 1: Outreach count (>0)
cutoff_30 = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
res_outreach = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_30).execute()
sent = res_outreach.count if res_outreach.count is not None else 0

# Step 4: Leads
res_leads = supabase.table("contacts_master").select("status", count="exact").in_("status", ["new", "research_done"]).execute()
lead_pool = res_leads.count if res_leads.count is not None else len(res_leads.data)

# Step 5: Heartbeat
cutoff_15 = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
res_hb = supabase.table("system_health_log").select("checked_at").gte("checked_at", cutoff_15).order("checked_at", desc=True).limit(1).execute()
hb_found = len(res_hb.data) > 0

# Campaign Mode
res_camp = supabase.table("system_state").select("status").eq("key", "campaign_mode").execute()
status = res_camp.data[0].get("status") if res_camp.data else "unknown"

output = {
    "outreach_30m": sent,
    "lead_pool": lead_pool,
    "heartbeat_working": hb_found,
    "campaign_mode": status
}

with open("verify_results.json", "w") as f:
    json.dump(output, f, indent=4)
