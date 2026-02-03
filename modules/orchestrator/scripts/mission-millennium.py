import os
import requests
import json
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(".env.local")

# Config
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
TRIGGER_URL = "https://nearmiss1193--ghl-omni-automation-ghl-webhook.modal.run"

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# 1,000 Lead Millennial Wave Grid
GRID = {
    # Florida (750 Leads)
    "Tampa": {"leads": 150, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    "Orlando": {"leads": 150, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    "Miami": {"leads": 150, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    "Jacksonville": {"leads": 150, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    "Sarasota": {"leads": 150, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    # Georgia (250 Leads)
    "Atlanta": {"leads": 125, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]},
    "Savannah": {"leads": 125, "industries": ["HVAC", "Plumbing", "Solar", "Electrician"]}
}

def ingest_millennium_wave():
    supabase = get_supabase()
    print("--- INITIATING MILLENNIUM SCALE (1,000 LEADS) ---")
    
    total_ingested = 0
    
    for city, data in GRID.items():
        print(f"\n📍 Deploying Millennium Wave to: {city}")
        leads_per_industry = data["leads"] // len(data["industries"])
        
        for industry in data["industries"]:
            print(f"   Sector: {industry} (Target: {leads_per_industry})")
            for i in range(1, leads_per_industry + 1):
                lead_name = f"{city} {industry} Millennium #{i}"
                contact_id = f"millen_{city.lower()[:3]}_{industry.lower()[:3]}_{i}"
                
                # 1. Ingest to Supabase
                payload = {
                    "ghl_contact_id": contact_id,
                    "full_name": lead_name,
                    "status": "new",
                    "website_url": f"https://{city.lower()}{industry.lower()}{i}-vortex.com"
                }
                supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
                total_ingested += 1
                
                # 2. Trigger Vortex (Strategic Pacing)
                # Trigger every 25th lead to manage enrichment load at scale
                if total_ingested % 25 == 0:
                    webhook_payload = {
                        "type": "ContactUpdate",
                        "contact_id": contact_id,
                        "name": lead_name,
                        "tags": ["trigger-vortex", f"city-{city.lower()}", "millennium-wave"]
                    }
                    try:
                        requests.post(TRIGGER_URL, json=webhook_payload)
                        print(f"🚀 [Millennium Wave] Vortex Triggered for {lead_name}")
                    except:
                        pass
                
                if i % 25 == 0:
                    print(f"      - {i} leads ingested for {industry}")

    print(f"\n--- MILLENNIUM WAVE INGESTION COMPLETE ({total_ingested} TARGETS) ---")

if __name__ == "__main__":
    ingest_millennium_wave()
