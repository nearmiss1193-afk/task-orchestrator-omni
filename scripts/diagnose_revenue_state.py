import os
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def check_table(endpoint, params):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{endpoint}", headers=headers, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error {r.status_code}: {r.text}")
        return None

print("=== REVENUE PIPELINE DIAGNOSTIC ===")

# 1. Outreach Count
touches = check_table("outbound_touches", {"select": "id", "limit": 100, "order": "ts.desc"})
print(f"1. Total recent outbound touches: {len(touches) if touches else 0}")

# 2. Campaign Mode
state = check_table("system_state", {"key": "eq.campaign_mode", "select": "status"})
print(f"2. Campaign Mode: {state[0].get('status') if state else 'unknown'}")

# 3. Available Leads
leads = check_table("contacts_master", {"status": "in.(new,research_done)", "select": "id", "limit": 10})
print(f"3. Contactable Leads (sample): {len(leads) if leads else 0}")

# 4. Heartbeats
health = check_table("system_health_log", {"select": "checked_at,status", "order": "checked_at.desc", "limit": 3})
if health:
    print(f"4. Last Heartbeats:")
    for h in health:
        print(f"   - {h['checked_at']} ({h['status']})")
else:
    print("4. Last Heartbeats: None found")
