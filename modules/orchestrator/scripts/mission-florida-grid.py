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

# 5 Cities x 4 Industries x 25 Leads = 500 Leads
CITIES = ["Tampa", "Orlando", "Miami", "Jacksonville", "Sarasota"]
INDUSTRIES = ["HVAC", "Plumbing", "Solar", "Electrician"]

def ingest_florida_grid():
    supabase = get_supabase()
    print("--- INITIATING FLORIDA WIDE BLITZ (500 LEADS) ---")
    
    for city in CITIES:
        print(f"\n📍 Deploying to City: {city}")
        for industry in INDUSTRIES:
            print(f"   Sector: {industry}")
            # Simulated large batch for demo scale
            for i in range(1, 26):
                lead_name = f"{city} {industry} Pros #{i}"
                contact_id = f"fl_blit_{city.lower()[:3]}_{industry.lower()[:3]}_{i}"
                
                # 1. Ingest to Supabase
                payload = {
                    "ghl_contact_id": contact_id,
                    "full_name": lead_name,
                    "status": "new",
                    "website_url": f"https://{city.lower()}{industry.lower()}{i}.com"
                }
                supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
                
                # 2. Trigger Vortex (Paced)
                # Only trigger every 5th lead for the first wave to avoid quota spikes
                if i % 5 == 0:
                    webhook_payload = {
                        "type": "ContactUpdate",
                        "contact_id": contact_id,
                        "name": lead_name,
                        "tags": ["trigger-vortex", f"city-{city.lower()}", "florida-blitz"]
                    }
                    try:
                        requests.post(TRIGGER_URL, json=webhook_payload)
                        print(f"🚀 [Wave 1] Vortex Triggered for {lead_name}")
                    except:
                        pass
                
                if i % 10 == 0:
                    print(f"      - {i} leads ingested for {industry} in {city}")

    print("\n--- FLORIDA GRID INGESTION COMPLETE (500 TARGETS) ---")

if __name__ == "__main__":
    ingest_florida_grid()
