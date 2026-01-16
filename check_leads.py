"""Quick check and trigger outreach"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# Check new leads
r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?status=eq.new&limit=20", headers=headers)
leads = r.json()
print(f"NEW leads ready for outreach: {len(leads)}")
for l in leads[:10]:
    print(f"  {l.get('company_name', '?')} | {l.get('phone', 'no phone')}")

if len(leads) == 0:
    print("\nNo NEW leads - checking all lead statuses...")
    r2 = requests.get(f"{SUPABASE_URL}/rest/v1/leads?select=status&limit=1000", headers=headers)
    all_leads = r2.json()
    statuses = {}
    for l in all_leads:
        s = l.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1
    print(f"Lead statuses: {statuses}")
