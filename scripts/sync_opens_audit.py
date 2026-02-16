
import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sync_historical_opens():
    print("🔄 SOVEREIGN SYNC: Synchronizing historical email opens...")
    
    # 1. Fetch all unique email_opens (limit 1000 for safety)
    r = requests.get(f"{SUPABASE_URL}/rest/v1/email_opens?select=email_id,opened_at&order=opened_at.asc&limit=1000", headers=HEADERS)
    if r.status_code != 200:
        print(f"❌ Failed to fetch opens: {r.text}")
        return
    
    opens = r.json()
    print(f"📊 Found {len(opens)} open records to process.")
    
    synced_count = 0
    
    for entry in opens:
        email_uid = entry.get("email_id")
        opened_at = entry.get("opened_at")
        
        if not email_uid:
            continue
            
        # 2. Find matching outbound_touch using payload->>email_uid
        # Note: We use the jsonb arrow operator in the query if supported, but here we query by payload containment or similar
        # Since we are using REST, we can filter by payload->email_uid
        query_url = f"{SUPABASE_URL}/rest/v1/outbound_touches?payload->>email_uid=eq.{email_uid}&opened=eq.false"
        r_touch = requests.get(query_url, headers=HEADERS)
        
        if r_touch.status_code == 200 and r_touch.json():
            touch = r_touch.json()[0]
            touch_id = touch.get("id")
            
            # 3. Update outbound_touches
            update_data = {
                "opened": True,
                "opened_at": opened_at
            }
            r_update = requests.patch(f"{SUPABASE_URL}/rest/v1/outbound_touches?id=eq.{touch_id}", headers=HEADERS, json=update_data)
            
            if r_update.status_code in [200, 204]:
                synced_count += 1
                if synced_count % 50 == 0:
                    print(f"📍 Synced {synced_count} records...")
        
    print(f"✅ SYNC COMPLETE: {synced_count} dashboard records updated.")

if __name__ == "__main__":
    sync_historical_opens()
