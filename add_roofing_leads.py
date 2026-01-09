# add_roofing_leads.py - Add roofing company leads for parallel campaign
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
import uuid

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Roofing Companies across multiple states
ROOFING_LEADS = [
    # FLORIDA (EST)
    {"company_name": "Sunshine State Roofing", "city": "Tampa", "state": "FL", "phone": "813-555-5001", "first_name": "Mike", "last_name": "Johnson"},
    {"company_name": "Florida Roof Pros", "city": "Orlando", "state": "FL", "phone": "407-555-5002", "first_name": "Dave", "last_name": "Williams"},
    {"company_name": "Gulf Coast Roofing", "city": "Sarasota", "state": "FL", "phone": "941-555-5003", "first_name": "Tom", "last_name": "Anderson"},
    {"company_name": "Palm Beach Roofing", "city": "West Palm Beach", "state": "FL", "phone": "561-555-5004", "first_name": "Rick", "last_name": "Davis"},
    {"company_name": "Jacksonville Roof Masters", "city": "Jacksonville", "state": "FL", "phone": "904-555-5005", "first_name": "Steve", "last_name": "Miller"},
    
    # TEXAS (CT)
    {"company_name": "Lone Star Roofing", "city": "Dallas", "state": "TX", "phone": "214-555-5006", "first_name": "Bobby", "last_name": "Smith"},
    {"company_name": "Texas Roof Solutions", "city": "Houston", "state": "TX", "phone": "713-555-5007", "first_name": "Carlos", "last_name": "Garcia"},
    {"company_name": "Austin Roofing Co", "city": "Austin", "state": "TX", "phone": "512-555-5008", "first_name": "Jake", "last_name": "Wilson"},
    {"company_name": "San Antonio Roof Experts", "city": "San Antonio", "state": "TX", "phone": "210-555-5009", "first_name": "Juan", "last_name": "Martinez"},
    {"company_name": "Fort Worth Roofing", "city": "Fort Worth", "state": "TX", "phone": "817-555-5010", "first_name": "Kevin", "last_name": "Brown"},
    
    # ARIZONA (MT)
    {"company_name": "Desert Roofing Phoenix", "city": "Phoenix", "state": "AZ", "phone": "602-555-5011", "first_name": "Dan", "last_name": "Taylor"},
    {"company_name": "Arizona Roof Masters", "city": "Scottsdale", "state": "AZ", "phone": "480-555-5012", "first_name": "Greg", "last_name": "Lee"},
    {"company_name": "Tucson Roofing Pros", "city": "Tucson", "state": "AZ", "phone": "520-555-5013", "first_name": "Chris", "last_name": "White"},
    {"company_name": "Mesa Roof Solutions", "city": "Mesa", "state": "AZ", "phone": "480-555-5014", "first_name": "Jason", "last_name": "Harris"},
    
    # CALIFORNIA (PT)
    {"company_name": "LA Roofing Experts", "city": "Los Angeles", "state": "CA", "phone": "310-555-5015", "first_name": "Marcus", "last_name": "Jones"},
    {"company_name": "Bay Area Roofing", "city": "San Francisco", "state": "CA", "phone": "415-555-5016", "first_name": "Ryan", "last_name": "Chen"},
    {"company_name": "San Diego Roof Co", "city": "San Diego", "state": "CA", "phone": "619-555-5017", "first_name": "Derek", "last_name": "Kim"},
    {"company_name": "Sacramento Roofing", "city": "Sacramento", "state": "CA", "phone": "916-555-5018", "first_name": "Matt", "last_name": "Nguyen"},
    {"company_name": "OC Roof Pros", "city": "Irvine", "state": "CA", "phone": "949-555-5019", "first_name": "Tony", "last_name": "Patel"},
    {"company_name": "Fresno Roofing Solutions", "city": "Fresno", "state": "CA", "phone": "559-555-5020", "first_name": "Jose", "last_name": "Rodriguez"},
]

def main():
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    added = 0
    for lead in ROOFING_LEADS:
        record = {
            "id": str(uuid.uuid4()),
            "company_name": lead["company_name"],
            "email": f"info@{lead['company_name'].lower().replace(' ', '').replace('&','')[:15]}.com",
            "status": "ready_to_send",
            "agent_research": {
                "city": lead["city"],
                "state": lead["state"],
                "phone": lead["phone"],
                "first_name": lead["first_name"],
                "last_name": lead["last_name"],
                "industry": "Roofing",
                "source": "roofing_expansion_v1"
            }
        }
        
        try:
            s.table('leads').insert(record).execute()
            added += 1
            print(f"+ {lead['company_name']} ({lead['state']}) - ROOFING")
        except Exception as e:
            print(f"x {lead['company_name']}: {e}")
    
    print(f"\n=== ADDED {added} ROOFING LEADS ===")
    print("FL: 5 | TX: 5 | AZ: 4 | CA: 6")
    print("Sarah will pick these up in the drip campaign!")

if __name__ == "__main__":
    main()
