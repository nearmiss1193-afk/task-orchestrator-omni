
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print("=== ALL VAPI ASSISTANTS ===")
url = "https://api.vapi.ai/assistant"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

res = requests.get(url, headers=headers)
if res.status_code == 200:
    assistants = res.json()
    print(f"Found {len(assistants)} assistants:\n")
    for a in assistants:
        print(f"  ID: {a.get('id')}")
        print(f"  Name: {a.get('name')}")
        print(f"  ---")
else:
    print(f"Error: {res.status_code} - {res.text}")
