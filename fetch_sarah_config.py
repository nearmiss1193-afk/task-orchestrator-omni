import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

res = requests.get(url, headers=headers)
if res.status_code == 200:
    with open("sarah_config_full.json", "w") as f:
        json.dump(res.json(), f, indent=4)
    print(f"Sarah configuration saved to sarah_config_full.json")
else:
    print(f"Error: {res.status_code} - {res.text}")
