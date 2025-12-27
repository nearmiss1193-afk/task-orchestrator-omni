
import os
import requests
import json
import time

# Hardcoded Credentials
URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/contacts_master"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def seed():
    print("--- SEEDING TEST DATA (DIRECT HTTP PROVEN) ---")
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Minimal Data
    leads = [
        {"name": "Alpha Corp", "person": "Alice Alpha", "email": "ceo@alpha.com"},
        {"name": "Beta Ltd", "person": "Bob Beta", "email": "vp@beta.com"},
        {"name": "Gamma Inc", "person": "Gary Gamma", "email": "owner@gamma.com"},
        {"name": "Delta LLC", "person": "Dana Delta", "email": "admin@delta.com"},
        {"name": "Omega Co", "person": "Oscar Omega", "email": "founder@omega.com"}
    ]
    
    for i, lead in enumerate(leads):
        try:
            # EXACT Payload structure from test_raw_insert.py (Response 201)
            payload = {
                "ghl_contact_id": f"seed_verified_{int(time.time())}_{i}",
                "full_name": lead["person"],
                "email": lead["email"],
                "status": "new"
            }
            
            resp = requests.post(URL, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                print(f"Inserted: {lead['person']}")
            else:
                print(f"Failed: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    seed()
