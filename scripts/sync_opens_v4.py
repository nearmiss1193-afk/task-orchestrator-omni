
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

def sync_v4():
    print("🚀 SOVEREIGN SYNC v4: Local Memory Matching...")
    
    # 1. Fetch all opens
    print("  [1/3] Fetching email_opens...")
    r_opens = requests.get(f"{SUPABASE_URL}/rest/v1/email_opens?select=email_id,recipient_email,opened_at&order=opened_at.desc&limit=2000", headers=HEADERS)
    opens = r_opens.json() if r_opens.status_code == 200 else []
    print(f"  Found {len(opens)} opens.")

    # 2. Fetch all outreach logs
    print("  [2/3] Fetching outbound_touches (email)...")
    r_touches = requests.get(f"{SUPABASE_URL}/rest/v1/outbound_touches?channel=eq.email&opened=eq.false&select=id,payload&limit=2000", headers=HEADERS)
    touches = r_touches.json() if r_touches.status_code == 200 else []
    print(f"  Found {len(touches)} un-opened touches.")

    # 3. Match locally
    print("  [3/3] Matching and updating...")
    synced = 0
    
    # Build a lookup for touches by email_uid and by 'to' address
    touch_lookup_uid = {}
    touch_lookup_email = {}
    
    for t in touches:
        tid = t.get("id")
        p = t.get("payload") or {}
        uid = p.get("email_uid")
        email_to = p.get("to")
        
        if uid: touch_lookup_uid[uid] = tid
        if email_to:
            if isinstance(email_to, list):
                for e in email_to: touch_lookup_email[e.lower().strip()] = tid
            else:
                touch_lookup_email[email_to.lower().strip()] = tid

    for entry in opens:
        uid = entry.get("email_id")
        email = entry.get("recipient_email")
        opened_at = entry.get("opened_at")
        
        target_tid = None
        if uid and uid in touch_lookup_uid:
            target_tid = touch_lookup_uid[uid]
        elif email and email.lower().strip() in touch_lookup_email:
            target_tid = touch_lookup_email[email.lower().strip()]
            
        if target_tid:
            # 4. Synchronous update (could batch, but let's see)
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/outbound_touches?id=eq.{target_tid}",
                headers=HEADERS,
                json={"opened": True, "opened_at": opened_at}
            )
            synced += 1
            # Remove from lookup to avoid duplicate updates if opens has multiple for same lead
            if uid in touch_lookup_uid: del touch_lookup_uid[uid]
            # (Email lookup removal ignored for simplicity)

    print(f"✅ SYNC v4 COMPLETE: {synced} outreach records recovered.")

if __name__ == "__main__":
    sync_v4()
