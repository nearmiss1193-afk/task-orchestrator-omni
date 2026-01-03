import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase() -> Client:
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def expand_seacoast_grid():
    """
    MISSION: EXPAND SILVER SHIELD PARTNER GRID
    Targets: Elder Law, VA Agencies, Specialized Placement.
    """
    print("--- MISSION: SILVER SHIELD GRID EXPANSION ---")
    
    partners = [
        {"name": "The Karpel Law Firm", "type": "Elder Law", "site": "tampaelderlaw.com"},
        {"name": "Florida Dept of Veterans Affairs (Tampa)", "type": "VA Agency", "site": "floridavets.org"},
        {"name": "A Place for Mom (Tampa Team)", "type": "Placement", "site": "aplaceformom.com"},
        {"name": "CarePatrol of Central FL", "type": "Placement", "site": "carepatrol.com"},
        {"name": "HALO Senior Solutions", "type": "Placement", "site": "haloseniorsolutions.com"},
        {"name": "Senior Choices of Florida", "type": "Placement", "site": "seniorchoicesfl.com"},
        {"name": "VA Regional Office (St. Petersburg)", "type": "VA Agency", "site": "va.gov/st-petersburg-regional-office/"}
    ]
    
    supabase = get_supabase()
    
    for p in partners:
        cid = f"seacoast_partner_{p['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        payload = {
            "ghl_contact_id": cid,
            "full_name": p['name'],
            "website_url": p['site'],
            "status": "new",
            "tags": ["seacoast_partner", "silver_shield", p['type']],
            "city": "Tampa"
        }
        
        try:
            supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
            print(f"✅ Ingested Partner: {p['name']} ({p['type']})")
        except Exception as e:
            print(f"❌ Failed to ingest {p['name']}: {str(e)}")

if __name__ == "__main__":
    expand_seacoast_grid()
