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

# 6 Industries x 10 Leads = 60 Lead Multi-Industry Blitz
INDUSTRIES = {
    "Solar": ["SunCity Solar", "Tampa Bay Power", "Gulf Coast Energy", "SolarTech Tampa", "Pure Power FL", "SunReady", "Bright Future", "Solar Edge Tampa", "EcoEnergy", "Peak Solar"],
    "Landscaping": ["GreenLeaf Tampa", "Palm Harbor Turf", "Elite Gardens", "Green Scene", "Landscape Pro", "Tampa Turf", "Lawn Masters", "Garden State FL", "Outdoor Oasis", "Green Horizon"],
    "Electricians": ["Current Pro Tampa", "Sparky Electric", "Volt Masters", "Power Surge", "ElectroLine", "Tampa Amp", "Wire Wise", "Shock Proof", "Grid Guard", "Flash Electric"],
    "Pest Control": ["BugsAway Tampa", "Shield Pest Force", "ClearChoice Pest", "Kill Zone", "Bug Stop", "Pest Free FL", "Safe Guard Pest", "EcoShield Tampa", "Zero Bugs", "Termite Tech"],
    "Moving": ["Swift Movers Tampa", "Elite Transit", "Gulf Shore Moves", "Easy Relocation", "Tampa Haul", "Move Fast", "Safe Way Movers", "City Transit", "Peak Packers", "Road Runner"],
    "Pool Maintenance": ["Vortex Pools Tampa", "Crystal Clear Maintenance", "Blue Water Pros", "Aqua Guard", "Pool Perfection", "Tampa Splash", "Clean Swim", "Sun Coast Pools", "Deep Blue", "Pool Care Elite"]
}

def ingest_blitz_leads():
    supabase = get_supabase()
    print("--- INITIATING SCALED MULTI-INDUSTRY BLITZ (6 SECTORS / 60 LEADS) ---")
    
    for industry, leads in INDUSTRIES.items():
        print(f"\nProcessing Sector: {industry}")
        for lead_name in leads:
            contact_id = f"blitz_scaled_{industry.lower()}_{lead_name.replace(' ', '_').lower()}"
            
            # 1. Ingest to Supabase
            payload = {
                "ghl_contact_id": contact_id,
                "full_name": lead_name,
                "status": "new",
                "website_url": f"https://{lead_name.replace(' ', '').lower()}.com"
            }
            supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
            print(f"✅ Ingested: {lead_name}")

            # 2. Trigger Vortex (Enrichment)
            webhook_payload = {
                "type": "ContactUpdate",
                "contact_id": contact_id,
                "name": lead_name,
                "website": f"https://{lead_name.replace(' ', '').lower()}.com",
                "tags": ["trigger-vortex", f"sector-{industry.lower()}", "scaled-mission"]
            }
            try:
                requests.post(TRIGGER_URL, json=webhook_payload)
                print(f"🚀 Vortex Triggered for {lead_name}")
            except:
                print(f"❌ Failed to trigger vortex for {lead_name}")

            time.sleep(0.5) # Balanced pacing for 60 leads

if __name__ == "__main__":
    ingest_blitz_leads()
