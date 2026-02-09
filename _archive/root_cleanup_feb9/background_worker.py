"""
STABILITY MOAT: BACKGROUND WORKER (RAILWAY)
Handles persistent 'Pulse' tasks: GHL Sync, Identity Swapping, and Health Checks.
Running on Railway to release Modal Cron slots.
"""
import os
import time
import sys
import requests
from datetime import datetime

# Ensure path is set for modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.supabase_client import get_supabase

def sync_ghl_contacts():
    """
    ZERO-TAX POLLING: Fetches new contacts from GHL every 5 minutes.
    """
    print(f"[{datetime.now().isoformat()}] 🔄 SYNC: Polling GHL for new contacts...")
    supabase = get_supabase()
    location_id = os.environ.get("GHL_LOCATION_ID")
    api_token = os.environ.get("GHL_API_TOKEN")

    if not location_id or not api_token:
        print("❌ Sync Error: Missing GHL credentials in environment")
        return

    # Fetch contacts
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit=20"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        contacts = response.json().get("contacts", [])
        print(f"📥 Found {len(contacts)} contacts in GHL.")

        for contact in contacts:
            ghl_id = contact.get("id")
            email = contact.get("email")
            phone = contact.get("phone")
            name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()

            # UPSERT into contacts_master
            data = {
                "ghl_id": ghl_id,
                "email": email,
                "phone": phone,
                "full_name": name,
                "status": "new",
                "source": "polling_sync",
                "meta": contact
            }
            
            supabase.table("contacts_master").upsert(data, on_conflict="ghl_id").execute()
            print(f"✅ Synced lead: {name}")

    except Exception as e:
        print(f"❌ Sync Failed: {e}")

def identity_audit():
    """
    GHL IDENTITY SWEEP: Ensures all leads in contacts_master have a GHL ID.
    If a lead is missing a GHL ID, it pushes them to GHL.
    """
    print(f"[{datetime.now().isoformat()}] 🆔 AUDIT: Checking for missing GHL IDs...")
    supabase = get_supabase()
    location_id = os.environ.get("GHL_LOCATION_ID")
    api_token = os.environ.get("GHL_API_TOKEN")
    
    if not location_id or not api_token:
        print("❌ Audit Error: Missing GHL credentials")
        return

    try:
        # Fetch leads without a GHL ID
        res = supabase.table("contacts_master").select("*").is_("ghl_id", "null").limit(5).execute()
        leads = res.data
        if not leads:
            print("✅ Audit: All processed leads have GHL IDs.")
            return

        print(f"🔄 Audit: Pushing {len(leads)} leads to GHL for Identity Link...")
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }

        for lead in leads:
            # Create contact in GHL
            url = "https://services.leadconnectorhq.com/contacts/"
            payload = {
                "locationId": location_id,
                "email": lead.get("email"),
                "phone": lead.get("phone"),
                "firstName": lead.get("full_name", "").split(" ")[0],
                "lastName": " ".join(lead.get("full_name", "").split(" ")[1:])
            }
            
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code in [200, 201]:
                ghl_id = resp.json().get("contact", {}).get("id")
                if ghl_id:
                    supabase.table("contacts_master").update({"ghl_id": ghl_id}).eq("id", lead["id"]).execute()
                    print(f"✅ Identity Linked: {lead.get('full_name')} -> {ghl_id}")
            elif resp.status_code == 400 and "already exists" in resp.text.lower():
                # Potential overlap, we'd ideally fetch the ID here
                print(f"⚠️ Lead already exists in GHL: {lead.get('email')}")
                # We could add an ID fetch here if needed
            else:
                print(f"❌ Identity Link Failed for {lead.get('full_name')}: {resp.status_code}")

    except Exception as e:
        print(f"❌ Audit Failed: {e}")

def main_loop():
    print("🚀 SOVEREIGN WORKER ONLINE (RAILWAY)")
    while True:
        try:
            sync_ghl_contacts()
            identity_audit()
        except Exception as e:
            print(f"🔥 Worker Crash Loop Error: {e}")
        
        # Sleep for 5 minutes (300 seconds)
        time.sleep(300)

if __name__ == "__main__":
    main_loop()
