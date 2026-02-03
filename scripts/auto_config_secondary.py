import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY")
SALES_ID = os.environ.get("VAPI_PHONE_NUMBER_ID")
NEW_URL = "https://nearmiss1193-afk--ghl-omni-automation-office-voice-tool-logic.modal.run"

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

print("🔍 Searching for available secondary line...")

try:
    resp = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    if resp.status_code == 200:
        numbers = resp.json()
        target = None
        
        for ph in numbers:
            pid = ph.get('id')
            if pid != SALES_ID:
                target = ph
                break
        
        if target:
            display_num = target.get('number') or target.get('phoneNumber')
            print(f"🎯 Found Candidate: {display_num} (ID: {target['id']})")
            
            # Configure
            patch_url = f"https://api.vapi.ai/phone-number/{target['id']}"
            patch_resp = requests.patch(patch_url, json={"serverUrl": NEW_URL}, headers=headers)
            
            if patch_resp.status_code == 200:
                print(f"✅ SUCCESS! Office Manager configured on: {display_num}")
                print(f"🔗 URL: {NEW_URL}")
            else:
                print(f"❌ Failed to patch: {patch_resp.text}")
        else:
            print("❌ No spare numbers available. Please buy one in Vapi Dashboard.")
            
    else:
        print(f"❌ Error listing numbers: {resp.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
