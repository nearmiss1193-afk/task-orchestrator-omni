"""Get Vapi phone numbers and attach Sarah to target number"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
TARGET_NUMBER = "8639465043"  # +1 863-946-5043

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# 1. Get all phone numbers
print("=== VAPI PHONE NUMBERS ===")
r = requests.get("https://api.vapi.ai/phone-number", headers=headers)
if r.ok:
    phones = r.json()
    print(f"Found {len(phones)} phone numbers:\n")
    target_found = None
    
    for p in phones:
        num = p.get('number', '')
        num_clean = num.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
        
        print(f"ID: {p.get('id')}")
        print(f"Number: {num}")
        print(f"SMS: {p.get('smsEnabled')}")
        print(f"Assistant: {p.get('assistantId')}")
        
        if TARGET_NUMBER in num_clean:
            target_found = p
            print(">>> THIS IS THE TARGET NUMBER <<<")
        print("---")
    
    # Attach Sarah to target if found
    if target_found:
        print(f"\n=== ATTACHING SARAH TO {target_found.get('number')} ===")
        patch_r = requests.patch(
            f"https://api.vapi.ai/phone-number/{target_found.get('id')}",
            headers=headers,
            json={
                "assistantId": SARAH_ID,
                "smsEnabled": True
            }
        )
        print(f"Result: {patch_r.status_code}")
        if patch_r.ok:
            print("SUCCESS! Sarah attached.")
            print(patch_r.json())
        else:
            print(f"ERROR: {patch_r.text}")
    else:
        print(f"\n!!! TARGET NUMBER {TARGET_NUMBER} NOT FOUND IN VAPI !!!")
        print("You need to import this number from Twilio or buy it through Vapi.")
else:
    print(f"ERROR: {r.status_code} - {r.text}")
