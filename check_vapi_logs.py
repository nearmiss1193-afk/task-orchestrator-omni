import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
url = "https://api.vapi.ai/call?limit=5"
headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}

print("--- RECENT VAPI CALL LOGS ---")
res = requests.get(url, headers=headers)
if res.status_code == 200:
    calls = res.json()
    for c in calls:
        print(f"ID: {c['id']} | Status: {c.get('status')} | Error: {c.get('error')} | Dest: {c.get('customer', {}).get('number')}")
else:
    print(f"Failed to fetch logs: {res.status_code}")
