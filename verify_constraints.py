import requests
import json
import uuid

# Hardcoded for fast debug
URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/conversation_events"
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

def get_valid_ids():
    r = requests.get("https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/conversations?limit=1", headers=HEADERS)
    if r.ok and r.json():
        return r.json()[0]["id"]
    return None

conv_id = get_valid_ids()
dummy_ghl_id = "test_ghl_id"

channels = ["sms", "call", "email", "webchat", "web", "chat", "other", "support", "google", "fb"]

for c in channels:
    print(f"\nTesting channel: {c}")
    data = {
        "conversation_id": conv_id, 
        "event_type": "note", 
        "source": "ghl", 
        "direction": "out", 
        "channel": c, 
        "external_id": str(uuid.uuid4()), 
        "ghl_contact_id": dummy_ghl_id
    }
    code, text = test_insert(data)
    print(f"Result: {code}")
    if code == 201:
        print(f"✅ SUCCESS! Valid channel is: {c}")
    else:
        print(f"Error: {text[:200]}")
