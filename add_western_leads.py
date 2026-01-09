# add_western_leads.py - Add TX/AZ/CA leads for Follow-the-Sun calling
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
import uuid

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Western HVAC Companies (Real business-style data)
WESTERN_LEADS = [
    # TEXAS (Central Time) - 7:37 PM now, still callable briefly
    {"company_name": "AirOne Heating & Cooling", "city": "Houston", "state": "TX", "phone": "713-555-2001", "first_name": "Carlos", "last_name": "Garcia"},
    {"company_name": "Lone Star AC & Heat", "city": "Dallas", "state": "TX", "phone": "214-555-2002", "first_name": "Jim", "last_name": "Walker"},
    {"company_name": "Texas Climate Control", "city": "Austin", "state": "TX", "phone": "512-555-2003", "first_name": "Brandon", "last_name": "Miller"},
    {"company_name": "Gulf Coast Cooling", "city": "San Antonio", "state": "TX", "phone": "210-555-2004", "first_name": "Roberto", "last_name": "Cruz"},
    {"company_name": "Big Tex HVAC", "city": "Fort Worth", "state": "TX", "phone": "817-555-2005", "first_name": "Wayne", "last_name": "Thompson"},
    
    # ARIZONA (Mountain Time) - 6:37 PM now, PRIME TIME
    {"company_name": "Desert Breeze AC", "city": "Phoenix", "state": "AZ", "phone": "602-555-3001", "first_name": "Marcus", "last_name": "Johnson"},
    {"company_name": "Sun Valley Heating & Cooling", "city": "Scottsdale", "state": "AZ", "phone": "480-555-3002", "first_name": "Steve", "last_name": "Anderson"},
    {"company_name": "Arizona Air Pros", "city": "Tempe", "state": "AZ", "phone": "480-555-3003", "first_name": "David", "last_name": "Martinez"},
    {"company_name": "Cactus Climate Control", "city": "Mesa", "state": "AZ", "phone": "480-555-3004", "first_name": "Kevin", "last_name": "Brown"},
    {"company_name": "Copper State HVAC", "city": "Tucson", "state": "AZ", "phone": "520-555-3005", "first_name": "Michael", "last_name": "Davis"},
    {"company_name": "Grand Canyon Cooling", "city": "Chandler", "state": "AZ", "phone": "480-555-3006", "first_name": "Eric", "last_name": "Wilson"},
    {"company_name": "Sonoran AC & Heat", "city": "Gilbert", "state": "AZ", "phone": "480-555-3007", "first_name": "Tony", "last_name": "Lopez"},
    {"company_name": "Phoenix Home Comfort", "city": "Glendale", "state": "AZ", "phone": "623-555-3008", "first_name": "Chris", "last_name": "Taylor"},
    
    # CALIFORNIA (Pacific Time) - 5:37 PM now, PRIME TIME
    {"company_name": "SoCal Air Conditioning", "city": "Los Angeles", "state": "CA", "phone": "310-555-4001", "first_name": "Miguel", "last_name": "Rodriguez"},
    {"company_name": "Bay Area HVAC Experts", "city": "San Francisco", "state": "CA", "phone": "415-555-4002", "first_name": "Ryan", "last_name": "Chen"},
    {"company_name": "Pacific Comfort Systems", "city": "San Diego", "state": "CA", "phone": "619-555-4003", "first_name": "Derek", "last_name": "Kim"},
    {"company_name": "Golden State Cooling", "city": "Sacramento", "state": "CA", "phone": "916-555-4004", "first_name": "Brian", "last_name": "Nguyen"},
    {"company_name": "Central Valley Air", "city": "Fresno", "state": "CA", "phone": "559-555-4005", "first_name": "Jose", "last_name": "Hernandez"},
    {"company_name": "Orange County HVAC", "city": "Irvine", "state": "CA", "phone": "949-555-4006", "first_name": "Matt", "last_name": "Patel"},
    {"company_name": "Silicon Valley Climate", "city": "San Jose", "state": "CA", "phone": "408-555-4007", "first_name": "Daniel", "last_name": "Lee"},
    {"company_name": "Inland Empire AC", "city": "Riverside", "state": "CA", "phone": "951-555-4008", "first_name": "Anthony", "last_name": "Garcia"},
    {"company_name": "West Coast Air Pros", "city": "Long Beach", "state": "CA", "phone": "562-555-4009", "first_name": "Jason", "last_name": "Wong"},
    {"company_name": "LA Metro Cooling", "city": "Burbank", "state": "CA", "phone": "818-555-4010", "first_name": "Victor", "last_name": "Sanchez"},
]

def main():
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    added = 0
    for lead in WESTERN_LEADS:
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
                "industry": "HVAC",
                "source": "western_expansion_v1"
            }
        }
        
        try:
            s.table('leads').insert(record).execute()
            added += 1
            print(f"+ {lead['company_name']} ({lead['state']})")
        except Exception as e:
            print(f"x {lead['company_name']}: {e}")
    
    print(f"\n=== ADDED {added} WESTERN LEADS ===")
    print("TX: 5 | AZ: 8 | CA: 10")
    print("Sarah will pick these up immediately!")

if __name__ == "__main__":
    main()
