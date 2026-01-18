#!/usr/bin/env python3
"""
FIX VAPI PHONES - Attach Sarah to ALL phone numbers for inbound
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# All our numbers that should have Sarah
TARGET_NUMBERS = [
    "3527585336",   # +1 (352) 758-5336 - CANONICAL
    "8632132505",   # +1 (863) 213-2505 - Rachel line
]

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

print("=== VAPI PHONE FIX - ATTACHING SARAH TO ALL NUMBERS ===\n")

r = requests.get("https://api.vapi.ai/phone-number", headers=headers)
if r.ok:
    phones = r.json()
    print(f"Found {len(phones)} phone numbers\n")
    
    fixed = 0
    for p in phones:
        phone_id = p.get('id')
        num = p.get('number', '')
        current_assistant = p.get('assistantId')
        sms_enabled = p.get('smsEnabled', False)
        
        print(f"📞 {num}")
        print(f"   ID: {phone_id}")
        print(f"   Current Assistant: {current_assistant or 'NONE'}")
        print(f"   SMS Enabled: {sms_enabled}")
        
        # Check if this needs fixing
        needs_fix = False
        if not current_assistant:
            print("   ⚠️ NO ASSISTANT - FIXING!")
            needs_fix = True
        elif current_assistant != SARAH_ID:
            print(f"   ⚠️ WRONG ASSISTANT - FIXING!")
            needs_fix = True
        
        if not sms_enabled:
            print("   ⚠️ SMS DISABLED - ENABLING!")
            needs_fix = True
        
        if needs_fix:
            patch_r = requests.patch(
                f"https://api.vapi.ai/phone-number/{phone_id}",
                headers=headers,
                json={
                    "assistantId": SARAH_ID,
                    "smsEnabled": True
                }
            )
            if patch_r.ok:
                print("   ✅ FIXED!")
                fixed += 1
            else:
                print(f"   ❌ Error: {patch_r.text[:100]}")
        else:
            print("   ✅ Already configured correctly")
        
        print()
    
    print(f"=== SUMMARY: Fixed {fixed} phone numbers ===")
else:
    print(f"ERROR: {r.status_code} - {r.text}")
