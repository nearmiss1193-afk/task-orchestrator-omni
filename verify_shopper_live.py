
import os
import time
from supabase import create_client
from dotenv import load_dotenv

# Force load .env from current directory
load_dotenv(".env")

import requests
import json
import datetime

def inject_lead(email):
    # url = os.environ.get("SUPABASE_URL")
    # key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    supabase = create_client(url, key)
    
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    ghl_id = f"test_hvac_{timestamp}"
    name = f"Red Team HVAC {timestamp}"
    
    payload = {
        "ghl_contact_id": ghl_id,
        "full_name": name,
        "email": email,
        "status": "new",
        "tags": ["trigger-vortex", "secret-shopper", "hvac"]
    }
    
    print(f"💉 Injecting HVAC Lead: {email}...", flush=True)
    
    # 1. DB Write
    try:
        supabase.table("contacts_master").upsert(payload).execute()
        print("   ✅ DB Write Success")
    except Exception as e:
        print(f"   ❌ DB Write Failed: {e}")
        return

    # 2. Webhook Trigger
    webhook_url = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"
    ghl_payload = {
        "type": "ContactUpdate",
        "contact_id": ghl_id,
        "location_id": "TEST_LOC",
        "contact": payload
    }
    
    try:
        requests.post(webhook_url, json=ghl_payload)
        print(f"   ✅ Webhook Fired: {webhook_url}")
    except Exception as e:
        print(f"   ⚠️ Webhook Failed: {e}")

def verify_live_lead(email):
    # url = os.environ.get("SUPABASE_URL")
    # key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    supabase = create_client(url, key)
    
    print(f"🔎 Monitoring DB for: {email}")
    
    for i in range(12): # Wait up to 60s
        print(f"   ...tick {i*5}s", flush=True)
        # Check Contacts
        res = supabase.table("contacts_master").select("*").eq("email", email).execute()
        if res.data:
            contact = res.data[0]
            cid = contact['ghl_contact_id']
            print(f"✅ Lead Captured! ID: {cid}")
            
            # Check Staged Reply (Spartan)
            reply_res = supabase.table("staged_replies").select("*").eq("contact_id", cid).execute()
            if reply_res.data:
                print(f"✅ Spartan Responded: {reply_res.data[0]['draft_content']}")
                return True
            else:
                print(f"⏳ Lead found, waiting for Spartan...")
        
        time.sleep(5)
        
    print("❌ Timeout or Spartan Asleep.", flush=True)
    return False

if __name__ == "__main__":
    # Expects to be run with a specific email argument or hardcoded for the session
    import sys
    target = "red_team_hvac_test@aiserviceco.com"
    inject_lead(target)
    verify_live_lead(target)
