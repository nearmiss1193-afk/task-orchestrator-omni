import requests
import json
import uuid

URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/conversations"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def test_insert(payload):
    try:
        r = requests.post(URL, headers=HEADERS, json=payload)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

# Get a valid contact_id
r = requests.get("https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/contact_profiles?limit=1", headers=HEADERS)
contact_id = r.json()[0]["id"]
print(f"Using Contact ID: {contact_id}")

tests = [
    {"channel": "sms", "status": "open"},
    {"channel": "SMS", "status": "open"},
    {"channel": "sms", "status": "OPEN"},
]

for t in tests:
    print(f"\nTesting: {t}")
    data = {
        "contact_id": contact_id,
        "channel": t["channel"],
        "status": t["status"]
    }
    code, text = test_insert(data)
    print(f"Result: {code}")
    if code == 201 or (code == 409 and "already exists" in text):
        print("SUCCESS (or duplicate)")
    else:
        print(f"Error: {text}")
