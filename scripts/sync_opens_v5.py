
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

def sync_v5():
    print("🚀 SOVEREIGN SYNC v5: Status-Based Matching (Bypass missing column)...")
    
    # 1. Fetch all opens
    r_opens = requests.get(f"{SUPABASE_URL}/rest/v1/email_opens?select=email_id,recipient_email,opened_at&order=opened_at.desc&limit=2000", headers=HEADERS)
    opens = r_opens.json() if r_opens.status_code == 200 else []
    print(f"  Found {len(opens)} opens.")

    # 2. Fetch all outreach logs (email)
    r_touches = requests.get(f"{SUPABASE_URL}/rest/v1/outbound_touches?channel=eq.email&status=eq.sent&select=id,payload&limit=2000", headers=HEADERS)
    touches = r_touches.json() if r_touches.status_code == 200 else []
    print(f"  Found {len(touches)} 'sent' touches.")

    # 3. Match and Update
    synced = 0
    touch_lookup_email = {}
    for t in touches:
        p = t.get("payload") or {}
        email_to = p.get("to")
        if email_to:
            if isinstance(email_to, list):
                for e in email_to: touch_lookup_email[e.lower().strip()] = t
            else:
                touch_lookup_email[email_to.lower().strip()] = t

    for entry in opens:
        email = entry.get("recipient_email")
        opened_at = entry.get("opened_at")
        if not email: continue
        
        email = email.lower().strip()
        if email in touch_lookup_email:
            touch = touch_lookup_email[email]
            tid = touch["id"]
            
            # Update payload + status
            new_payload = touch.get("payload") or {}
            new_payload["opened"] = True
            new_payload["opened_at"] = opened_at
            
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/outbound_touches?id=eq.{tid}",
                headers=HEADERS,
                json={
                    "status": "opened",
                    "payload": new_payload
                }
            )
            synced += 1
            del touch_lookup_email[email]

    print(f"✅ SYNC v5 COMPLETE: {synced} outreach records recovered and status modernized.")

if __name__ == "__main__":
    sync_v5()
