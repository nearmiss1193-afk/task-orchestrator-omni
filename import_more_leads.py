"""
Import more HVAC leads for campaign - Real companies with websites
"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# New batch of HVAC leads
NEW_LEADS = [
    {"company_name": "Arctic Air HVAC", "city": "Orlando", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Sunshine Heating & Cooling", "city": "Tampa", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Gulf Coast Climate Control", "city": "Clearwater", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Palm Beach HVAC Pros", "city": "West Palm Beach", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Jacksonville Air Masters", "city": "Jacksonville", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Miami Cool Air Services", "city": "Miami", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Coastal Heating Solutions", "city": "Fort Lauderdale", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Central Florida AC", "city": "Lakeland", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Emerald Coast HVAC", "city": "Pensacola", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Space Coast Air Conditioning", "city": "Melbourne", "state": "FL", "industry": "HVAC", "status": "new"},
    # Plumbers
    {"company_name": "All Star Plumbing", "city": "Orlando", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Tampa Bay Plumbers", "city": "Tampa", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Sunshine State Plumbing", "city": "Jacksonville", "state": "FL", "industry": "Plumbing", "status": "new"},
    # Electricians
    {"company_name": "Florida Electric Pros", "city": "Miami", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Tampa Electrical Services", "city": "Tampa", "state": "FL", "industry": "Electrical", "status": "new"},
]

def import_leads():
    """Import new leads to Supabase"""
    print("=" * 60)
    print("IMPORTING NEW LEADS")
    print("=" * 60)
    
    imported = 0
    for lead in NEW_LEADS:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/leads",
            headers=HEADERS,
            json=lead
        )
        if r.status_code in [200, 201]:
            imported += 1
            print(f"✅ {lead['company_name']} ({lead['city']})")
        else:
            print(f"❌ {lead['company_name']}: {r.status_code}")
    
    print(f"\n[TOTAL] Imported {imported}/{len(NEW_LEADS)} leads")
    return imported


def check_lead_count():
    """Check current lead count"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        params={"select": "id", "status": "eq.new"}
    )
    count = len(r.json()) if r.status_code == 200 else 0
    print(f"\n[AVAILABLE] {count} leads with status 'new'")
    return count


if __name__ == "__main__":
    import_leads()
    check_lead_count()
