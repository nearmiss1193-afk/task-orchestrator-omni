import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
url = "https://api.vapi.ai/phone-number"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

# CONFIGURATION (To be populated after reading vapi_phones.json)
# Format: {"PHONE_ID": "ASSISTANT_ID"}
ASSIGNMENTS = {
    # 1. Sarah (HVAC) -> +18636928474
    "c2afdc74-8d2a-4ebf-8736-7eecc1992204": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
    
    # 2. Riley (ALF) -> +19045129565
    "4e38087a-0937-4997-bc1c-4ddf77c5cf70": "93f64b69-314c-4040-b8d2-1c9f9a71dfc8"
}

def update_number(phone_id, assistant_id):
    if "PHONE_ID" in phone_id:
        print(f"Skipping placeholder {phone_id}")
        return

    update_url = f"{url}/{phone_id}"
    payload = {"assistantId": assistant_id}
    
    try:
        response = requests.patch(update_url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Assigned Assistant {assistant_id} to Phone {phone_id}")
    except Exception as e:
        print(f"❌ Error updating {phone_id}: {e}")

if __name__ == "__main__":
    print("🔄 Starting Phone Assignment...")
    for phone_id, assistant_id in ASSIGNMENTS.items():
        update_number(phone_id, assistant_id)
    print("✨ Assignment Complete.") 
