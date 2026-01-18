#!/usr/bin/env python3
"""
ADD TEST CONTACTS WITH PHONE NUMBERS - FIXED COLUMN NAMES
"""
import os
import requests
import uuid
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Test HVAC contacts with real-ish phone numbers
test_contacts = [
    {"name": "Cool Air HVAC", "phone": "+18135551001", "email": "test1@coolairhvac.com"},
    {"name": "Sunshine Heating", "phone": "+18135551002", "email": "test2@sunshine.com"},
    {"name": "Arctic Breeze AC", "phone": "+18135551003", "email": "test3@arcticbreeze.com"},
    {"name": "Comfort Zone HVAC", "phone": "+18135551004", "email": "test4@comfortzone.com"},
    {"name": "Pro Climate Control", "phone": "+18135551005", "email": "test5@proclimate.com"},
]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

print("=== ADDING TEST CONTACTS WITH PHONES ===\n")

for c in test_contacts:
    payload = {
        "id": str(uuid.uuid4()),
        "ghl_contact_id": f"test_{uuid.uuid4().hex[:8]}",
        "phone": c["phone"],
        "email": c["email"],
        "status": "new",
        "raw_research": {"company_name": c["name"], "vertical": "hvac"}
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/contacts_master",
        headers=headers,
        json=payload
    )
    
    if r.status_code in [200, 201]:
        print(f"✅ Added: {c['name']} - {c['phone']}")
    else:
        print(f"❌ Failed {c['name']}: {r.status_code} - {r.text[:100]}")

print("\n=== DONE ===")
