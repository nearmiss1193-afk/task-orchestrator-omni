import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def list_assistants():
    print("🔍 Listing Assistants...")
    res = requests.get("https://api.vapi.ai/assistant", headers=HEADERS)
    if res.status_code == 200:
        assistants = res.json()
        with open("ASSISTANTS_DUMP.json", "w") as f:
            json.dump(assistants, f, indent=2)
        print("✅ Dumped assistants to ASSISTANTS_DUMP.json")
    else:
        print(f"❌ Failed: {res.text}")

if __name__ == "__main__":
    list_assistants()
