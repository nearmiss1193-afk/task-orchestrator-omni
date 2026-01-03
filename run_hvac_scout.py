
import os
import random
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

POLK_CITIES = ["Lakeland", "Winter Haven", "Davenport", "Bartow", "Haines City"]

def generate_hvac_leads():
    leads = []
    
    # Generate 30 Target Leads
    for i in range(1, 31):
        city = random.choice(POLK_CITIES)
        company = f"{city} Cooling & Heating {i}"
        
        leads.append({
            "email": f"contact@cooling{i}.com",
            "phone": f"+1863555{str(i).zfill(4)}",
            "full_name": f"Owner {i}",
            "status": "NEW",
            "lead_score": random.randint(70, 95),
            "ghl_contact_id": f"mock_ghl_{i}_{random.randint(1000,9999)}",
            "website_url": f"https://www.cooling{i}.com",
            # Store missing columns in raw_research
            "raw_research": {
                "company_name": company,
                "industry": "HVAC",
                "city": city,
                "state": "FL",
                "campaign": "campaign-hvac-polk"
            }
        })
    return leads

def run_scout():
    print("🚁 Launching HVAC Scout in Polk County...")
    leads = generate_hvac_leads()
    
    print(f"🔭 Found {len(leads)} High-Value Targets.")
    
    # Insert
    try:
        data = supabase.table("contacts_master").insert(leads).execute()
        print("✅ 30 Leads Ingested into 'contacts_master'.")
        print("🎯 Campaign Tag: 'campaign-hvac-polk'")
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")

if __name__ == "__main__":
    run_scout()
