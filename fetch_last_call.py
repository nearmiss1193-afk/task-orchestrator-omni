import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

url = "https://api.vapi.ai/call"
res = requests.get(url, headers=headers)

if res.status_code == 200:
    calls = res.json()
    if calls:
        last_call = calls[0]
        print(f"Fetch Success: {last_call.get('id')}")
        with open("last_call.json", "w") as f:
            json.dump(last_call, f, indent=4)
    else:
        print("No calls found.")
else:
    print(f"Error: {res.status_code} - {res.text}")
