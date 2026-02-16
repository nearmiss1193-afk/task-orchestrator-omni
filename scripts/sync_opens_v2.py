
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

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

def sync_v2():
    print("🔄 SOVEREIGN SYNC v2: Email-to-Phone Mapping...")
    
    # 1. Fetch all opens (last 1000)
    r = requests.get(f"{SUPABASE_URL}/rest/v1/email_opens?select=recipient_email,opened_at&order=opened_at.desc&limit=1000", headers=HEADERS)
    opens = r.json() if r.status_code == 200 else []
    print(f"📊 Found {len(opens)} opens.")

    processed = 0
    synced = 0
    
    # Cache for email -> phone mapping to save hits
    email_phone_map = {}

    for entry in opens:
        email = entry.get("recipient_email")
        opened_at = entry.get("opened_at")
        if not email: continue
        
        email = email.lower().strip()
        
        # 2. Map Email to Phone via contacts_master
        if email not in email_phone_map:
            r_contact = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?email=eq.{email}&select=phone", headers=HEADERS)
            data = r_contact.json()
            if data and data[0].get("phone"):
                email_phone_map[email] = data[0]["phone"]
            else:
                email_phone_map[email] = None
        
        phone = email_phone_map.get(email)
        if not phone: continue
        
        # 3. Update outbound_touches where channel=email and phone matches and opened=false
        r_update = requests.patch(
            f"{SUPABASE_URL}/rest/v1/outbound_touches?phone=eq.{phone}&channel=eq.email&opened=eq.false",
            headers=HEADERS,
            json={"opened": True, "opened_at": opened_at}
        )
        
        if r_update.status_code in [200, 204]:
            synced += 1
        
        processed += 1
        if processed % 100 == 0:
            print(f"📍 Processed {processed} opens, synced {synced}...")

    print(f"✅ SYNC v2 COMPLETE: {synced} outreach records recovered.")

if __name__ == "__main__":
    sync_v2()
