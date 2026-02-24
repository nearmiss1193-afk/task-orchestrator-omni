"""
Campaign Projections + Solar Lead Audit
"""
import os, sys, json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

results = {}

# --- TODAY'S ACTIVITY BY CHANNEL ---
today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()

emails_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel", "email").gte("ts", today_start).execute()
sms_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel", "sms").gte("ts", today_start).execute()
calls_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel", "call").gte("ts", today_start).execute()

results["today_emails"] = emails_today.count or 0
results["today_sms"] = sms_today.count or 0
results["today_calls"] = calls_today.count or 0
results["today_total"] = (emails_today.count or 0) + (sms_today.count or 0) + (calls_today.count or 0)

# --- FRESH LEADS ---
fresh = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
results["fresh_leads"] = fresh.count or 0

# Leads with email
with_email = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).neq("email", "").execute()
results["fresh_with_email"] = with_email.count or 0

# Leads with website (eligible for audit)
with_website = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).neq("website_url", "").execute()
results["fresh_with_website"] = with_website.count or 0

# --- PROJECTION MATH ---
# Orchestrator runs every 5 min, processes 15 leads per cycle
# Business hours: 8 AM - 6 PM EST = 10 hours = 120 cycles
# Email: 24/7 = 288 cycles/day * 15 = 4320 max
# SMS window: 8AM-6PM = 120 cycles * up to 15 = limited by GHL IDs
# Calls: max 3 per cycle * 120 = 360 max
cycles_remaining_today = max(0, int((18 - 8.5) * 12))  # 8:30 AM to 6 PM, 12 cycles/hr
results["cycles_remaining"] = cycles_remaining_today
results["projected_email_max"] = min(results["fresh_with_email"], cycles_remaining_today * 15)
results["projected_sms_max"] = min(results["fresh_leads"], cycles_remaining_today * 5)  # fewer have GHL IDs
results["projected_calls_max"] = min(360, cycles_remaining_today * 3)

# --- SOLAR LEADS ---
solar_by_niche = supabase.table("contacts_master").select("id,company_name,email,phone,status,niche").ilike("niche", "%solar%").execute()
solar_by_name = supabase.table("contacts_master").select("id,company_name,email,phone,status,niche").ilike("company_name", "%solar%").execute()

# Deduplicate by id
solar_map = {}
for s in (solar_by_niche.data or []) + (solar_by_name.data or []):
    solar_map[s["id"]] = s

solar_leads = list(solar_map.values())
results["solar_count"] = len(solar_leads)
results["solar_leads"] = solar_leads[:15]  # first 15 for display

# --- PROSPECTOR STATE ---
prospect_state = supabase.table("system_state").select("status").eq("key", "last_prospect_half_hour").execute()
results["prospector_last_key"] = prospect_state.data[0].get("status") if prospect_state.data else "NEVER_RUN"

with open("projections.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("Done: projections.json")
