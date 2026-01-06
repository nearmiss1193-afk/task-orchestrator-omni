import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
url = "https://api.vapi.ai/call?limit=2"
headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}

res = requests.get(url, headers=headers)
if res.status_code == 200:
    calls = res.json()
    for c in calls:
        call_id = c['id']
        detail_url = f"https://api.vapi.ai/call/{call_id}"
        detail_res = requests.get(detail_url, headers=headers)
        if detail_res.status_code == 200:
            d = detail_res.json()
            print(f"\n--- CALL ID: {call_id} ---")
            print(f"Assistant: {d.get('assistant', {}).get('name')}")
            print(f"Status: {d.get('status')}")
            print(f"Transcript:\n{d.get('transcript', 'No transcript found.')}")
            print(f"Tool Calls: {json.dumps(d.get('toolCalls', []), indent=2)}")
else:
    print(f"Failed to fetch logs: {res.status_code}")
