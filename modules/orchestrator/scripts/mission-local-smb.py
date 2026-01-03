import os
import json
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(".env.local")

# Config
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def trigger_modal_enrichment(contact_id: str, name: str, website: str, email: str):
    # This triggers the Modal function via web endpoint or remote call
    # For now, we simulate the webhook trigger or use the remote call logic
    webhook_url = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"
    payload = {
        "type": "ContactUpdate",
        "contact_id": contact_id,
        "tags": ["trigger-vortex", "smb-local"],
        "name": name,
        "website": website,
        "email": email
    }
    try:
        requests.post(webhook_url, json=payload)
        print(f"✅ Triggered Modal Enrichment for {contact_id}")
    except Exception as e:
        print(f"❌ Failed to trigger Modal: {e}")

def run_mission():
    supabase = get_supabase()
    
    leads = [
        {"id": "smb_tampa_001", "name": "ACS Home Services", "website": "https://acshomeservices.com", "email": "info@acshomeservices.com"},
        {"id": "smb_tampa_002", "name": "Cass Plumbing", "website": "https://cassplumbingtampabay.com", "email": "service@cassplumbing.com"},
        {"id": "smb_tampa_003", "name": "SouthShore Roofing", "website": "https://southshorecontractorstampa.com", "email": "hello@southshoreroofing.com"},
        {"id": "smb_tampa_004", "name": "Olin Plumbing", "website": "https://plumberstampa.com", "email": "office@olinplumbing.com"},
        {"id": "smb_tampa_005", "name": "Del-Air Heating & AC", "website": "https://delair.com", "email": "leads@delair.com"}
    ]

    print("--- MISSION: LOCAL SMB INGESTION ---")
    
    for lead in leads:
        # Upsert lead
        res = supabase.table("contacts_master").upsert({
            "ghl_contact_id": lead['id'],
            "full_name": lead['name'],
            "website_url": lead['website'],
            "email": lead['email'],
            "status": "new"
        }, on_conflict="ghl_contact_id").execute()
        
        print(f"✅ Ingested {lead['name']}")
        
        # Trigger Enrichment
        trigger_modal_enrichment(lead['id'], lead['name'], lead['website'], lead['email'])

if __name__ == "__main__":
    run_mission()
