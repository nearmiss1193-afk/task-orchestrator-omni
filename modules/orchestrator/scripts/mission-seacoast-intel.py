import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase() -> Client:
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def predator_intel_hunt():
    """
    MISSION: FIND REFERRAL PARTNERS FOR SEACOAST
    Targets: VA Social Workers, Elder Law, Discharge Planners in Tampa.
    """
    print("--- MISSION: SILVER SHIELD INTEL HUNT ---")
    
    # Target entities for scraping/manual verification
    targets = [
        {"name": "James A. Haley Veterans Hospital", "city": "Tampa", "type": "VA Hospital"},
        {"name": "AdventHealth Tampa Discharge", "city": "Tampa", "type": "Hospital"},
        {"name": "Tampa General Hospital Social Work", "city": "Tampa", "type": "Hospital"},
        {"name": "VFW Post 424", "city": "Tampa", "type": "Veteran Group"},
        {"name": "VFW Post 8108", "city": "Riverview", "type": "Veteran Group"},
        {"name": "Hill & Associates Elder Law", "city": "Tampa", "type": "Elder Law"},
        {"name": "The Karpel Law Firm", "city": "Tampa", "type": "Elder Law"}
    ]
    
    supabase = get_supabase()
    
    for t in targets:
        # Simulate ingest with 'predator' tags for follow-up
        ghl_id = f"seacoast_partner_{t['name'].lower().replace(' ', '_')}"
        
        payload = {
            "ghl_contact_id": ghl_id,
            "full_name": t['name'],
            "website_url": "https://www.google.com/search?q=" + t['name'].replace(' ', '+'),
            "status": "new",
            "tags": ["seacoast_partner", "silver_shield", t['type']],
            "city": t['city']
        }
        
        try:
            supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
            print(f"✅ Ingested Partner: {t['name']} ({t['type']})")
        except Exception as e:
            print(f"❌ Failed to ingest {t['name']}: {str(e)}")

if __name__ == "__main__":
    predator_intel_hunt()
