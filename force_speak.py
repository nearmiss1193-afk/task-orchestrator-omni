
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

print(f"--- FORCE SPEAKER TEST ---")
print(f"Target: {phone}")
print(f"Location: {loc}")

headers = {
    "Authorization": f"Bearer {token}",
    "Version": "2021-07-28",
    "Content-Type": "application/json"
}

# 1. Lookup Contact to get ID
print("1. Looking up Contact ID...")
search_url = f"https://services.leadconnectorhq.com/contacts/search/duplicate?locationId={loc}&number={phone}"
res = requests.get(search_url, headers=headers)

contact_id = None
if res.status_code == 200:
    data = res.json()
    if data.get('contact'):
        contact_id = data['contact']['id']
        print(f"   [FOUND] Contact ID: {contact_id}")
    else:
        print(f"   [404] Contact not found by phone.")
else:
    print(f"   [ERR] Lookup Failed: {res.text}")

# 2. Send Message
if contact_id:
    print(f"2. Sending Test SMS...")
    msg_url = "https://services.leadconnectorhq.com/conversations/messages"
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": "This is a FORCED TEST message from Sovereign Command. If you get this, OUTBOUND is working."
    }
    res = requests.post(msg_url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        print(f"   [SUCCESS] Message Sent! ID: {res.json().get('conversationId')}")
    else:
        print(f"   [FAIL] Send Error: {res.status_code} - {res.text}")
else:
    print("Skipping send due to missing Contact ID.")
