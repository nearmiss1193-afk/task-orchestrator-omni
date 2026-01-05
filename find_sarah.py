
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print("=== ALL VAPI ASSISTANTS (FULL) ===")
url = "https://api.vapi.ai/assistant"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

res = requests.get(url, headers=headers)
if res.status_code == 200:
    assistants = res.json()
    print(f"Total: {len(assistants)} assistants\n")
    for i, a in enumerate(assistants):
        name = a.get('name', 'Unnamed')
        aid = a.get('id', 'No ID')
        # Check if name contains Sarah, Sara, or Spartan
        is_sarah = any(x in name.lower() for x in ['sarah', 'sara', 'spartan'])
        marker = " <<<< SARAH?" if is_sarah else ""
        print(f"{i+1}. {name}: {aid}{marker}")
else:
    print(f"Error: {res.status_code} - {res.text}")
