
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

token = os.environ.get("GHL_API_TOKEN")
loc = os.environ.get("GHL_LOCATION_ID")
phone = "+13529368152"

print("=== GHL-ONLY SMS TEST (VERBOSE) ===")
print(f"Token: {token[:10]}...")
print(f"Location: {loc}")
print(f"Target: {phone}")

headers = {
    "Authorization": f"Bearer {token}",
    "Version": "2021-07-28",
    "Content-Type": "application/json"
}

# 1. Find Contact
print("\n[1] Finding Contact...")
search_url = f"https://services.leadconnectorhq.com/contacts/search/duplicate?locationId={loc}&number={phone}"
res = requests.get(search_url, headers=headers)
print(f"   Status: {res.status_code}")
print(f"   Response: {res.text[:200]}")

contact_id = None
if res.status_code == 200:
    data = res.json()
    if data.get('contact'):
        contact_id = data['contact']['id']
        print(f"   Contact ID: {contact_id}")

# 2. Send SMS
if contact_id:
    print("\n[2] Sending SMS...")
    msg_url = "https://services.leadconnectorhq.com/conversations/messages"
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": "GHL Direct Test. Reply OK if received. Time: " + str(os.popen('time /t').read().strip())
    }
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    res = requests.post(msg_url, headers=headers, json=payload)
    print(f"   Status: {res.status_code}")
    print(f"   Response: {res.text}")
else:
    print("   [SKIP] No Contact ID found.")

print("\n=== DONE ===")
