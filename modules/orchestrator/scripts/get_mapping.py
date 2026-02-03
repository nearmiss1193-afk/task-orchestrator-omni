import os
import requests
from dotenv import load_dotenv

env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\task-orchestrator\.env.local"
load_dotenv(env_path)

def get_mapping():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    headers = {"Authorization": f"Bearer {token}", "Version": "2021-07-28"}
    url = f"https://services.leadconnectorhq.com/locations/{location_id}/customFields"
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        fields = res.json().get("customFields", [])
        for f in fields:
            name = f.get('name')
            if name in ["Annual Loss Projection", "Vortex Audit Link"]:
                print(f"{name}: {f.get('id')}")

if __name__ == "__main__":
    get_mapping()
