
import os
import requests
from dotenv import load_dotenv

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

def sync_v3():
    print("🔄 SOVEREIGN SYNC v3: Direct Payload Matching...")
    
    # 1. Fetch all opens (last 1000)
    r = requests.get(f"{SUPABASE_URL}/rest/v1/email_opens?select=recipient_email,opened_at&order=opened_at.desc&limit=1000", headers=HEADERS)
    opens = r.json() if r.status_code == 200 else []
    print(f"📊 Found {len(opens)} opens.")

    synced = 0
    processed = 0

    for entry in opens:
        email = entry.get("recipient_email")
        opened_at = entry.get("opened_at")
        if not email: continue
        
        # 2. Update outbound_touches dashboard (Direct Sync by payload->>to)
        # We target records where payload contains the email in the 'to' field
        r_update = requests.patch(
            f"{SUPABASE_URL}/rest/v1/outbound_touches?payload->>to=eq.{email}&opened=eq.false",
            headers=HEADERS,
            json={"opened": True, "opened_at": opened_at}
        )
        
        if r_update.status_code in [200, 204]:
            synced += 1
        
        processed += 1
        if processed % 100 == 0:
            print(f"📍 Processed {processed} opens, synced {synced}...")

    print(f"✅ SYNC v3 COMPLETE: {synced} outreach records recovered.")

if __name__ == "__main__":
    sync_v3()
