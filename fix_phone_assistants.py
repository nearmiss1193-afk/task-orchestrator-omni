"""
EMERGENCY FIX - Assign assistants to ALL phone numbers
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

# Sarah's ID - our main sales assistant
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# Fallback number (owner's phone)
FALLBACK_NUMBER = "+13529368152"

print("="*60)
print("EMERGENCY FIX - ASSIGNING ASSISTANTS TO ALL NUMBERS")
print("="*60)

# Get all phone numbers
r = requests.get('https://api.vapi.ai/phone-number', headers=headers)
phones = r.json()

fixed = 0
for p in phones:
    num = p.get('number')
    current_assistant = p.get('assistantId')
    phone_id = p.get('id')
    
    print(f"\n{num}:")
    print(f"  Current Assistant: {current_assistant or 'NONE'}")
    
    if not current_assistant:
        print(f"  FIXING - Assigning Sarah...")
        
        # Update phone to use Sarah
        update = requests.patch(
            f"https://api.vapi.ai/phone-number/{phone_id}",
            headers=headers,
            json={
                "assistantId": SARAH_ID,
                "fallbackDestination": {
                    "type": "number",
                    "number": FALLBACK_NUMBER
                }
            }
        )
        
        if update.ok:
            print(f"  SUCCESS - Sarah now answers this line!")
            fixed += 1
        else:
            print(f"  ERROR: {update.status_code} - {update.text[:100]}")
    else:
        print(f"  OK - Already has assistant")

print("\n" + "="*60)
print(f"FIXED: {fixed} phone numbers now have Sarah assigned")
print("="*60)
