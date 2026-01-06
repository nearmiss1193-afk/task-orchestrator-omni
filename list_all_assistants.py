import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
url = "https://api.vapi.ai/assistant"
headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}

print("[VAPI] Listing all assistants...")
res = requests.get(url, headers=headers)

if res.status_code == 200:
    assistants = res.json()
    print(f"Found {len(assistants)} assistants.")
    for a in assistants:
        print(f"ID: {a['id']} | Name: {a.get('name')} | Created: {a.get('createdAt')}")
    
    with open("ALL_ASSISTANTS.json", "w") as f:
        json.dump(assistants, f, indent=2)
    print("Full dump saved to ALL_ASSISTANTS.json")
else:
    print(f"❌ Failed: {res.status_code}")
    print(res.text)
