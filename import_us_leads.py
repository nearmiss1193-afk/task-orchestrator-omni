"""
Add US-Based HVAC Leads to Supabase
These are sample leads with US phone numbers (avoiding Canadian area codes)
"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# US HVAC leads - various cities with valid US area codes
US_LEADS = [
    {
        "company_name": "Comfort Air Solutions",
        "email": "info@comfortairsolutions.com",
        "phone": "+1 (813) 555-0147",  # Tampa FL
        "city": "Tampa",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Phoenix Climate Control",
        "email": "service@phoenixclimate.com",
        "phone": "+1 (602) 555-0189",  # Phoenix AZ
        "city": "Phoenix",
        "state": "AZ",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Dallas Heating & Cooling",
        "email": "quotes@dallashvac.com",
        "phone": "+1 (214) 555-0162",  # Dallas TX
        "city": "Dallas",
        "state": "TX",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Miami Comfort Systems",
        "email": "contact@miamicomfort.com",
        "phone": "+1 (305) 555-0134",  # Miami FL
        "city": "Miami",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Orlando HVAC Pros",
        "email": "service@orlandohvacpros.com",
        "phone": "+1 (407) 555-0198",  # Orlando FL
        "city": "Orlando",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Atlanta Air Experts",
        "email": "info@atlantaairexperts.com",
        "phone": "+1 (404) 555-0156",  # Atlanta GA
        "city": "Atlanta",
        "state": "GA",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Charlotte Climate Care",
        "email": "quotes@charlotteclimate.com",
        "phone": "+1 (704) 555-0173",  # Charlotte NC
        "city": "Charlotte",
        "state": "NC",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Jacksonville Cooling Co",
        "email": "service@jaxcooling.com",
        "phone": "+1 (904) 555-0141",  # Jacksonville FL
        "city": "Jacksonville",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Houston HVAC Masters",
        "email": "info@houstonhvacmasters.com",
        "phone": "+1 (713) 555-0188",  # Houston TX
        "city": "Houston",
        "state": "TX",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "San Antonio Air Services",
        "email": "contact@sanantonioair.com",
        "phone": "+1 (210) 555-0167",  # San Antonio TX
        "city": "San Antonio",
        "state": "TX",
        "industry": "HVAC",
        "status": "new"
    }
]

def main():
    print("=" * 60)
    print("IMPORTING US-BASED HVAC LEADS")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for lead in US_LEADS:
        try:
            resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/leads",
                headers=headers,
                json=lead,
                timeout=15
            )
            
            if resp.status_code in [200, 201]:
                print(f"  [OK] {lead['company_name']} - {lead['city']}, {lead['state']}")
                success += 1
            else:
                print(f"  [FAIL] {lead['company_name']}: {resp.status_code} - {resp.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {lead['company_name']}: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"IMPORTED: {success} leads | FAILED: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
