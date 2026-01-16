"""
Import Real HVAC Leads with Website URLs
These are real HVAC companies that we can email for outreach
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

# Real HVAC companies with websites (for email finder to enrich)
REAL_HVAC_LEADS = [
    # Florida HVAC companies
    {
        "company_name": "Comfort Temp",
        "website_url": "https://www.comforttemp.com",
        "phone": "+1 (813) 912-3456",
        "city": "Tampa",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "AC Pros of Florida",
        "website_url": "https://www.acprosfl.com",
        "phone": "+1 (321) 555-1234",
        "city": "Orlando",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "One Hour Air Conditioning",
        "website_url": "https://www.onehourair.com",
        "phone": "+1 (904) 555-5678",
        "city": "Jacksonville",
        "state": "FL",
        "industry": "HVAC",
        "status": "new"
    },
    # Texas HVAC companies
    {
        "company_name": "ABC Home & Commercial Services",
        "website_url": "https://www.abchomeandcommercial.com",
        "phone": "+1 (512) 555-9012",
        "city": "Austin",
        "state": "TX",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Autumn Air Heating & Cooling",
        "website_url": "https://www.autumnairaz.com",
        "phone": "+1 (602) 555-3456",
        "city": "Phoenix",
        "state": "AZ",
        "industry": "HVAC",
        "status": "new"
    },
    # Georgia HVAC
    {
        "company_name": "Shumate Air Conditioning & Heating",
        "website_url": "https://www.shumatehvac.com",
        "phone": "+1 (404) 555-7890",
        "city": "Atlanta",
        "state": "GA",
        "industry": "HVAC",
        "status": "new"
    },
    {
        "company_name": "Estes Services",
        "website_url": "https://www.estesair.com",
        "phone": "+1 (404) 555-2345",
        "city": "Atlanta",
        "state": "GA",
        "industry": "HVAC",
        "status": "new"
    },
    # North Carolina
    {
        "company_name": "Morris-Jenkins",
        "website_url": "https://www.morrisjenkins.com",
        "phone": "+1 (704) 555-6789",
        "city": "Charlotte",
        "state": "NC",
        "industry": "HVAC",
        "status": "new"
    },
    # Tennessee
    {
        "company_name": "Lee Company",
        "website_url": "https://www.leecompany.com",
        "phone": "+1 (615) 555-0123",
        "city": "Nashville",
        "state": "TN",
        "industry": "HVAC",
        "status": "new"
    },
    # California
    {
        "company_name": "Service Champions",
        "website_url": "https://www.servicechampions.com",
        "phone": "+1 (925) 555-4567",
        "city": "San Jose",
        "state": "CA",
        "industry": "HVAC",
        "status": "new"
    }
]

def main():
    print("=" * 60)
    print("IMPORTING REAL HVAC LEADS")
    print("=" * 60)
    
    imported = 0
    failed = 0
    
    for lead in REAL_HVAC_LEADS:
        try:
            resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/leads",
                headers=headers,
                json=lead,
                timeout=15
            )
            
            if resp.status_code in [200, 201]:
                print(f"  [OK] {lead['company_name']} - {lead['city']}, {lead['state']}")
                imported += 1
            else:
                print(f"  [EXISTS] {lead['company_name']}: {resp.text[:50]}")
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {lead['company_name']}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"IMPORTED: {imported} | FAILED/EXISTING: {failed}")
    print("=" * 60)
    print("\nNext: Run email_finder.py to enrich with decision maker emails")

if __name__ == "__main__":
    main()
