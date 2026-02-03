import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def upsert_contact(contact_data):
    """
    Upsert a contact into Supabase 'contacts_master' table.
    """
    url = f"{SUPABASE_URL}/rest/v1/contacts_master"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    response = requests.post(url, headers=headers, json=contact_data)
    if response.status_code in [200, 201]:
        print(f"[SUCCESS] Upserted: {contact_data['full_name']}")
        return True
    else:
        print(f"[ERROR] Failed to upsert {contact_data['full_name']}: {response.text}")
        return False

def trigger_modal_enrichment(lead):
    """
    Simulate GHL Webhook to trigger enrichment.
    """
    webhook_url = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"
    payload = {
        "type": "ContactUpdate",
        "contact_id": lead['ghl_contact_id'],
        "tags": ["trigger-vortex", "predator-active"],
        "name": lead['full_name'],
        "email": lead['email'],
        "website": lead['website_url']
    }
    
    # Note: Our webhook currently routes ContactUpdate to sync. 
    # To trigger research_lead_logic, we can either:
    # 1. Update webhook logic in deploy.py to trigger research on tag.
    # 2. Call the Modal function directly if authenticated.
    
    # For this mission, we'll assume the webhook handles the sync, 
    # but the REAL trigger is the 'trigger-vortex' tag presence.
    
    print(f"-> Sending trigger for {lead['ghl_contact_id']}...")
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print(f"   [OK] Trigger sent.")
        return True
    else:
        print(f"   [FAIL] Webhook status: {response.status_code}")
        return False

# MISSION TARGETS
LEADS = [
    {"full_name": "Nextdoor Ad Sales", "website_url": "https://nextdoor.com", "email": "ads@nextdoor.com", "ghl_contact_id": "mission_fs_001"},
    {"full_name": "DoorDash Enterprise Ads", "website_url": "https://doordash.com", "email": "ads@doordash.com", "ghl_contact_id": "mission_fs_002"},
    {"full_name": "Block (Cash App) Ads", "website_url": "https://block.xyz", "email": "ads@block.xyz", "ghl_contact_id": "mission_fs_003"},
    {"full_name": "WPP / Grey Group", "website_url": "https://grey.com", "email": "info@grey.com", "ghl_contact_id": "mission_fs_004"},
    {"full_name": "Podean", "website_url": "https://podean.com", "email": "hello@podean.com", "ghl_contact_id": "mission_fs_005"},
    {"full_name": "NewGen Influencer Agency", "website_url": "https://newgen.agency", "email": "contact@newgen.agency", "ghl_contact_id": "mission_fs_006"},
    {"full_name": "Critical Mass NYC", "website_url": "https://criticalmass.com", "email": "info@criticalmass.com", "ghl_contact_id": "mission_fs_007"}
]

def run_mission():
    print("--- MISSION: FIRST STRIKE INITIALIZED ---")
    for lead in LEADS:
        # Step 1: Ingest
        if upsert_contact(lead):
            # Step 2: Trigger (Simulated for now, would be GHL Tag hook in real life)
            trigger_modal_enrichment(lead)
    
    print("--- MISSION: FIRST STRIKE COMPLETED ---")
    print("Check Modal Logs and Supabase for enrichment results.")

if __name__ == "__main__":
    run_mission()
