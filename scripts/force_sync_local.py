import os
import requests
import json
from supabase import create_client, Client

# --- CREDENTIALS ---
# Using env vars if available, otherwise falling back
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

GHL_TOKEN = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"
LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"

def force_sync_client():
    print("🚀 STARTING LOCAL FORCE SYNC (CLIENT MODE)...")
    
    # Init Client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Client Init Failed: {e}")
        return

    # 1. Fetch GHL
    print("📥 Fetching GHL Contacts...")
    ghl_url = f"https://services.leadconnectorhq.com/contacts/?limit=100&locationId={LOCATION_ID}"
    ghl_headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    
    contacts = []
    try:
        res = requests.get(ghl_url, headers=ghl_headers)
        if res.status_code != 200:
            print(f"❌ GHL Error {res.status_code}: {res.text}")
            return
        contacts = res.json().get('contacts', [])
        print(f"📦 Fetched {len(contacts)} contacts from GHL.")
    except Exception as e:
        print(f"❌ GHL Exception: {e}")
        return

    if not contacts:
        print("⚠️ No contacts to sync.")
        return

    # 2. Push to Supabase (Client Upsert)
    count = 0
    batch = []
    
    for c in contacts:
        try:
            cid = c.get('id')
            name = c.get('name') or f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() or "Unknown"
            if name == "Unknown": continue 
            
            # Sanitization
            email = c.get('email') or ""
            phone = c.get('phone') or ""
            
            payload = {
                "ghl_contact_id": cid,
                "full_name": name,
                "email": email,
                # "phone": phone,
                # "tags": c.get('tags', []),
                "status": "new",
                # "lead_score": 10
            }
            batch.append(payload)
            count += 1
        except Exception as e:
            print(f"Skipping row: {e}")
            pass
            
    # Send Batch
    if batch:
        print(f"📤 Uploading {len(batch)} records to Supabase...")
        try:
            # Using upsert
            res = supabase.table("contacts_master").upsert(batch, on_conflict="ghl_contact_id").execute()
            print(f"✅ BATCH SUCCESS. {len(batch)} Leads Synced.")
        except Exception as e:
            print(f"❌ Supabase Upload Failed: {e}")

if __name__ == "__main__":
    force_sync_client()
