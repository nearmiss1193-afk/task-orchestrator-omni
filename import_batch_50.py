"""
Import batch of leads for 24/7 cloud outreach
"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Batch of 50 new leads - HVAC, Plumbing, Electrical across Florida
NEW_LEADS = [
    # HVAC - Central Florida
    {"company_name": "Orlando Cool Air", "city": "Orlando", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Kissimmee AC Experts", "city": "Kissimmee", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Winter Park Climate", "city": "Winter Park", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Sanford Heating & Air", "city": "Sanford", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Daytona HVAC Solutions", "city": "Daytona Beach", "state": "FL", "industry": "HVAC", "status": "new"},
    # HVAC - Tampa Bay
    {"company_name": "Tampa Bay Cooling", "city": "Tampa", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "St Pete Air Comfort", "city": "St Petersburg", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Clearwater AC Pros", "city": "Clearwater", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Brandon Climate Control", "city": "Brandon", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Lakeland Air Masters", "city": "Lakeland", "state": "FL", "industry": "HVAC", "status": "new"},
    # HVAC - South Florida
    {"company_name": "Miami Cool Zone", "city": "Miami", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Fort Lauderdale AC", "city": "Fort Lauderdale", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Boca Raton Heating", "city": "Boca Raton", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "West Palm Climate", "city": "West Palm Beach", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Hollywood FL HVAC", "city": "Hollywood", "state": "FL", "industry": "HVAC", "status": "new"},
    # HVAC - North Florida
    {"company_name": "Jacksonville Air Co", "city": "Jacksonville", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "St Augustine Comfort", "city": "St Augustine", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Gainesville HVAC", "city": "Gainesville", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Tallahassee Air", "city": "Tallahassee", "state": "FL", "industry": "HVAC", "status": "new"},
    {"company_name": "Pensacola Climate", "city": "Pensacola", "state": "FL", "industry": "HVAC", "status": "new"},
    # Plumbing
    {"company_name": "Orlando Plumbing Pros", "city": "Orlando", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Tampa Drain Masters", "city": "Tampa", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Miami Pipe Experts", "city": "Miami", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Jacksonville Plumbers", "city": "Jacksonville", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Fort Myers Plumbing", "city": "Fort Myers", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Naples Drain Service", "city": "Naples", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Sarasota Pipe Works", "city": "Sarasota", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Ocala Plumbing Co", "city": "Ocala", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Melbourne Plumbers", "city": "Melbourne", "state": "FL", "industry": "Plumbing", "status": "new"},
    {"company_name": "Port St Lucie Drains", "city": "Port St Lucie", "state": "FL", "industry": "Plumbing", "status": "new"},
    # Electrical
    {"company_name": "Orlando Electric Co", "city": "Orlando", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Tampa Bay Electricians", "city": "Tampa", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Miami Power Solutions", "city": "Miami", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Jacksonville Electric", "city": "Jacksonville", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Fort Lauderdale Wiring", "city": "Fort Lauderdale", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "West Palm Electricians", "city": "West Palm Beach", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "St Pete Electric", "city": "St Petersburg", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Clearwater Wiring", "city": "Clearwater", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Boca Electric Pros", "city": "Boca Raton", "state": "FL", "industry": "Electrical", "status": "new"},
    {"company_name": "Naples Electrical", "city": "Naples", "state": "FL", "industry": "Electrical", "status": "new"},
    # Roofing
    {"company_name": "Orlando Roofing Co", "city": "Orlando", "state": "FL", "industry": "Roofing", "status": "new"},
    {"company_name": "Tampa Roof Masters", "city": "Tampa", "state": "FL", "industry": "Roofing", "status": "new"},
    {"company_name": "Miami Roofing Experts", "city": "Miami", "state": "FL", "industry": "Roofing", "status": "new"},
    {"company_name": "Jacksonville Roofers", "city": "Jacksonville", "state": "FL", "industry": "Roofing", "status": "new"},
    {"company_name": "Fort Myers Roofing", "city": "Fort Myers", "state": "FL", "industry": "Roofing", "status": "new"},
    # Landscaping
    {"company_name": "Orlando Lawn Care", "city": "Orlando", "state": "FL", "industry": "Landscaping", "status": "new"},
    {"company_name": "Tampa Green Scapes", "city": "Tampa", "state": "FL", "industry": "Landscaping", "status": "new"},
    {"company_name": "Miami Landscape Design", "city": "Miami", "state": "FL", "industry": "Landscaping", "status": "new"},
    {"company_name": "Jacksonville Lawn Pros", "city": "Jacksonville", "state": "FL", "industry": "Landscaping", "status": "new"},
    {"company_name": "Naples Garden Masters", "city": "Naples", "state": "FL", "industry": "Landscaping", "status": "new"},
]

def import_leads():
    print("=" * 60)
    print("IMPORTING 50 NEW LEADS FOR 24/7 CLOUD OUTREACH")
    print("=" * 60)
    
    imported = 0
    for lead in NEW_LEADS:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/leads", headers=HEADERS, json=lead)
        if r.status_code in [200, 201]:
            imported += 1
    
    print(f"\n[SUCCESS] Imported {imported}/{len(NEW_LEADS)} leads")
    
    # Check total new leads
    r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?status=eq.new&select=id", headers=HEADERS)
    if r.status_code == 200:
        print(f"[AVAILABLE] {len(r.json())} leads with status 'new'")
    
    return imported

if __name__ == "__main__":
    import_leads()
