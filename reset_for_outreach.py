"""Reset 15 leads to NEW for immediate outreach - East Coast NOW"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}

# Get 15 contacted leads with phones
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/leads?status=eq.contacted&phone=not.is.null&limit=15&select=id,company_name,phone",
    headers=headers
)
leads = r.json()
print(f"Found {len(leads)} contacted leads with phones")

if len(leads) == 0:
    # Try called status
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?status=eq.called&phone=not.is.null&limit=15&select=id,company_name,phone",
        headers=headers
    )
    leads = r.json()
    print(f"Found {len(leads)} called leads with phones")

# Reset to NEW
reset_ids = [l['id'] for l in leads[:15]]
print(f"\nResetting {len(reset_ids)} leads to NEW status...")

for lid in reset_ids:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lid}",
        headers=headers,
        json={"status": "new"}
    )
    if r.status_code < 300:
        print(f"  ✓ Reset lead {lid}")
    else:
        print(f"  ✗ Failed: {r.status_code}")

print(f"\n✅ {len(reset_ids)} leads ready for outreach!")
print("\nRun: python check_leads.py to verify")
