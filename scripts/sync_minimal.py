import os
import requests
from supabase import create_client, Client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
# Correct Token & Location
GHL_TOKEN = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"
LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"

def sync_minimal():
    print("🚀 STARTING MINIMAL SYNC...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch 1 Contact
    url = f"https://services.leadconnectorhq.com/contacts/?limit=1&locationId={LOCATION_ID}"
    headers = {'Authorization': f'Bearer {GHL_TOKEN}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
    
    try:
        res = requests.get(url, headers=headers)
        c = res.json()['contacts'][0]
        print(f"📦 Got Contact: {c.get('email')}")
        
        # MINIMAL PAYLOAD
        payload = {
            "ghl_contact_id": c.get('id'),
            "status": "new"
            # Skipping full_name, email, tags, etc.
        }
        
        print(f"📤 Inserting Payload: {payload}")
        supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
        print("✅ SUCCESS.")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    sync_minimal()
