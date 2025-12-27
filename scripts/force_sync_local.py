import os
import requests
import json

# --- CREDENTIALS (VERIFIED) ---
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/contacts_master"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

GHL_TOKEN = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"
LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"

def force_sync_http():
    print("🚀 STARTING LOCAL FORCE SYNC (HTTP RAW MODE)...")
    
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

    # 2. Push to Supabase (Raw HTTP)
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # UPSERT MAGIC
    }
    
    count = 0
    batch = []
    
    for c in contacts:
        try:
            cid = c.get('id')
            name = c.get('name') or f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() or "Unknown"
            if name == "Unknown": continue 
            
            payload = {
                "ghl_contact_id": cid,
                "full_name": name,
                "email": c.get('email'),
                "phone": c.get('phone'),
                "tags": c.get('tags', []),
                "status": "new",
                "lead_score": 10
            }
            batch.append(payload)
            count += 1
        except:
            pass
            
    # Send Batch
    if batch:
        print(f"📤 Uploading {len(batch)} records to Supabase...")
        try:
            r = requests.post(SUPABASE_URL, headers=sb_headers, json=batch)
            if r.status_code in [200, 201]:
                print(f"✅ BATCH SUCCESS. {len(batch)} Leads Synced.")
            else:
                print(f"❌ Supabase Error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"❌ Supabase Upload Failed: {e}")

if __name__ == "__main__":
    force_sync_http()
