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
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
TARGET_NUMBER = "+18632132505"

def fix_routing():
    print(f"🔍 Auditing Route for {TARGET_NUMBER}...")
    
    # 1. Find the Phone ID
    res = requests.get("https://api.vapi.ai/phone-number", headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Failed to list numbers: {res.text}")
        return

    numbers = res.json()
    phone_id = None
    current_assistant = None
    
    for num in numbers:
        if num.get('number') == TARGET_NUMBER:
            phone_id = num.get('id')
            current_assistant = num.get('assistantId')
            print(f"✅ Found Phone ID: {phone_id}")
            print(f"   Current Assistant: {current_assistant}")
            break
            
    if not phone_id:
        print("❌ Number not found in Vapi account!")
        return

    # 2. Force Update if needed
    if current_assistant != ASSISTANT_ID:
        print(f"⚠️ Mismatch! Expected {ASSISTANT_ID}")
        print("🛠️ Updating Routing...")
        payload = {
            "assistantId": ASSISTANT_ID
        }
        patch_res = requests.patch(f"https://api.vapi.ai/phone-number/{phone_id}", headers=HEADERS, json=payload)
        if patch_res.status_code == 200:
            print("✅ SUCCESS: Number re-routed to Office Manager.")
        else:
            print(f"❌ Update Failed: {patch_res.text}")
    else:
        print("✅ Routing is CORRECT (Points to Office Manager).")
        print("🤔 If it still forwards, checking Assistant Config...")
        
        # Check Assistant for forwarding rules (rare but possible via tools/serverUrl)
        a_res = requests.get(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS)
        if a_res.status_code == 200:
            a_data = a_res.json()
            print(f"   Assistant First Message: {a_data.get('firstMessage')}")
            # Ensure it's not set to voicemaill endpoint
        
if __name__ == "__main__":
    fix_routing()
