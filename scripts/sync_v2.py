import os
import requests
import asyncio
from supabase import create_client, Client

# --- CREDENTIALS (VERIFIED) ---
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GHL_TOKEN = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"
LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"

def sync_v2():
    print("🚀 STARTING SYNC V2 (CLIENT MODE)...")
    
    # 1. Connect Supabase
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase Client Initialized")
        
        # PROBE: Check Table Access
        print("🕵️ Probing contacts_master...")
        probe = supabase.table("contacts_master").select("*", count="exact", head=True).execute()
        print(f"✅ Probe Successful. Count: {probe.count}")
        
    except Exception as e:
        print(f"❌ Supabase Connection/Probe Failed: {e}")
        # Proceeding anyway to see distinct error
        
    # 2. Fetch GHL
    print("📥 Fetching GHL Contacts...")
    ghl_url = f"https://services.leadconnectorhq.com/contacts/?limit=100&locationId={LOCATION_ID}"
    headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    
    try:
        res = requests.get(ghl_url, headers=headers)
        if res.status_code != 200:
            print(f"❌ GHL Error {res.status_code}: {res.text}")
            return
            
        data = res.json()
        contacts = data.get('contacts', [])
        print(f"📦 Fetched {len(contacts)} contacts from GHL.")
        
    except Exception as e:
        print(f"❌ GHL Request Failed: {e}")
        return

    if not contacts:
        print("⚠️ No contacts found in GHL.")
        return

    # 3. Upsert Logic
    success_count = 0
    fail_count = 0
    
    for c in contacts:
        try:
            cid = c.get('id')
            name = c.get('name') or f"{c.get('firstName', '')} {c.get('lastName', '')}".strip() or "Unknown"
            
            # Skip if really unknown, but keep if email exists
            if name == "Unknown" and not c.get('email'):
                continue
                
            payload = {
                "ghl_contact_id": cid,
                "full_name": name,
                "email": c.get('email'),
                "phone": c.get('phone'),
                # "tags": c.get('tags', []), # Suspect
                "status": "new",
                # "lead_score": 10 # Suspect
            }
            
            # Using the client to upsert
            supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
            print(f"   ✅ Synced: {name}")
            success_count += 1
            
        except Exception as e:
            # print(f"   ❌ Failed {c.get('id')}: {e}")
            print(f"   ❌ Failed {c.get('id')}: {e}")
            fail_count += 1
            
    print(f"🏁 SYNC COMPLETE. Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    sync_v2()
