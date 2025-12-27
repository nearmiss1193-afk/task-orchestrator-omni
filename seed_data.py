
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
    
    # CHAOS DATA (Resilience Test)
    leads = [
        {"name": "Chaos 1", "person": "No Email Guy", "email": ""}, # Missing Email
        {"name": "Chaos 2", "person": "", "email": "ghost@beta.com"}, # Missing Name
        {"name": "Chaos 3", "person": "D'Angelo O'Connor", "email": "complex@names.com"}, # Special Chars
        {"name": "Chaos 4", "person": "Robert'); DROP TABLE students;--", "email": "sql@inject.com"}, # SQL Injection Attempt
        {"name": "Chaos 5", "person": "Standard User", "email": "control@group.com"} # Control
    ]
    
    for i, lead in enumerate(leads):
        try:
            # Chaos Payload
            payload = {
                "ghl_contact_id": f"chaos_{int(time.time())}_{i}",
                "full_name": lead["person"] or "Unknown", # Handle missing name logic
                "email": lead["email"] or f"missing_{int(time.time())}@void.com", # Handle missing email
                "status": "new",
                "tags": ["chaos_test", "risk_high"]
            }
            
            resp = requests.post(URL, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                print(f"✅ Ingested: {payload['full_name']}")
            else:
                print(f"⚠️ Rejected (Expected?): {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    seed()
