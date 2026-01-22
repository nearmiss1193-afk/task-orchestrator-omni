import json
import os
from supabase import create_client, Client

def load_env():
    env_path = ".env.local"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        os.environ[parts[0]] = parts[1]

# Manually set environment variables if not in .env.local
os.environ["NEXT_PUBLIC_SUPABASE_URL"] = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'
os.environ["GHL_API_TOKEN"] = 'pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199'

SUB_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")

def get_supabase() -> Client:
    return create_client(SUB_URL, SUB_KEY)

def create_ghl_contact(lead):
    """Creates a contact in GHL and returns the contact ID."""
    url = "https://services.leadconnectorhq.com/contacts/"
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Version": "2021-04-15",
        "Content-Type": "application/json"
    }
    payload = {
        "firstName": lead.get("name", "Founder"),
        "website": lead.get("website", ""),
        "tags": ["predator-prospect", lead.get("niche", "cold-lead")],
        "locationId": "RnK4OjX0oDcqtWw0VyLr" # Extracted from manifest
    }
    
    try:
        import requests
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            return res.json().get("contact", {}).get("id")
        else:
            print(f"⚠️ GHL Contact Error: {res.text}")
            return None
    except Exception as e:
        print(f"❌ GHL Request Failed: {str(e)}")
        return None

def push_leads():
    enriched_file = "execution/enriched_batch_100.json"
    if not os.path.exists(enriched_file):
        print(f"❌ File not found: {enriched_file}")
        return

    with open(enriched_file, "r") as f:
        leads = json.load(f)

    supabase = get_supabase()
    print(f"🚀 Processing leads (GHL + Supabase)...")

    pushed_count = 0
    # Process a small slice to ensure success
    for lead in leads[:20]: 
        # 1. Create in GHL
        ghl_id = create_ghl_contact(lead)
        if not ghl_id:
            print(f"⏩ Skipping {lead.get('name')} (GHL Ingestion Failed)")
            continue
            
        # 2. Map fields to EXACT database schema
        # Schema: ['id', 'created_at', 'ghl_contact_id', 'full_name', 'email', 'phone', 'website', 'niche', 'sentiment', 'assigned_to', 'workflow_step', 'raw_research', 'ai_strategy', 'status']
        data = {
            "ghl_contact_id": ghl_id,
            "full_name": lead.get("name", "Founder"),
            "status": "research_done"
        }
        
        try:
            # Using simple insert for compatibility
            res = supabase.table("contacts_master").insert(data).execute()
            pushed_count += 1
            print(f"✅ Synced: {lead.get('name')} (GHL: {ghl_id})")
        except Exception as e:
            print(f"⚠️ Supabase Sync Error for {lead.get('name')}: {str(e)}")

    print(f"🏁 Successfully synced {pushed_count} leads.")

if __name__ == "__main__":
    push_leads()
