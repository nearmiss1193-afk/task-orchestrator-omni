# check_call_status.py - Check recent Vapi call statuses
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

print("=" * 50)
print("RECENT VAPI CALLS (Last 10)")
print("=" * 50)

# Get recent calls
res = requests.get("https://api.vapi.ai/call?limit=10", headers=headers)

if res.status_code == 200:
    calls = res.json()
    for c in calls:
        print(f"\nCall ID: {c.get('id', 'Unknown')[:20]}...")
        print(f"  Status: {c.get('status')}")
        print(f"  Type: {c.get('type')}")
        print(f"  Created: {c.get('createdAt', 'Unknown')[:19]}")
        print(f"  To: {c.get('customer', {}).get('number', 'Unknown')}")
        print(f"  Phone ID: {c.get('phoneNumberId', 'None')[:20]}..." if c.get('phoneNumberId') else "  Phone ID: None")
        
        # Check for errors
        if c.get('endedReason'):
            print(f"  Ended Reason: {c.get('endedReason')}")
        
        # Check costs
        if c.get('cost'):
            print(f"  Cost: ${c.get('cost')}")
else:
    print(f"Error: {res.status_code}")
    print(res.text)

# Check account status
print("\n" + "=" * 50)
print("CHECKING IF NUMBER CAN MAKE OUTBOUND CALLS")
print("=" * 50)

# Check the 2nd phone number details
SECOND_PHONE_ID = "40379c46-4b27-45de-8294-4908b694dfc6"
res2 = requests.get(f"https://api.vapi.ai/phone-number/{SECOND_PHONE_ID}", headers=headers)

if res2.status_code == 200:
    phone = res2.json()
    print(f"\nPhone: {phone.get('number')}")
    print(f"Provider: {phone.get('provider')}")
    print(f"Status: {phone.get('status', 'Unknown')}")
    print(f"Assistant: {phone.get('assistantId', 'None')}")
    
    # Check if there's any restriction
    if phone.get('twilioPhoneNumberSid'):
        print(f"Twilio SID: {phone.get('twilioPhoneNumberSid')}")
    if phone.get('vonagePhoneNumberId'):
        print(f"Vonage ID: {phone.get('vonagePhoneNumberId')}")
        
    print("\n[!] If no calls going through, the number may need:")
    print("    - Carrier registration in Vapi dashboard")
    print("    - A2P 10DLC registration for US numbers")
    print("    - Account billing/credits")
else:
    print(f"Error: {res2.status_code}")
