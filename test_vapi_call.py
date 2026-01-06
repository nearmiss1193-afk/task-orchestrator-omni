#!/usr/bin/env python3
"""Get Vapi phone ID and make test call"""
import requests

# Read key
key = None
with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'VAPI_PRIVATE_KEY' in line and '=' in line:
            key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

if not key:
    print("No VAPI key found")
    exit(1)

print(f"Key: {key[:15]}...")

# Get phone numbers
r = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {key}'})
print(f"\nPhone numbers response: {r.status_code}")

if r.status_code == 200:
    phones = r.json()
    if phones:
        phone = phones[0]
        print(f"\nPhone Number: {phone.get('number')}")
        print(f"Phone ID: {phone.get('id')}")
        print(f"Provider: {phone.get('provider')}")
        
        # Now make the test call
        print("\n" + "="*40)
        print("MAKING TEST CALL TO COMMANDER")
        print("="*40)
        
        call_response = requests.post(
            'https://api.vapi.ai/call/phone',
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            },
            json={
                'assistantId': '1a797f12-e2dd-4f7f-b2c5-08c38c74859a',  # Sarah
                'phoneNumberId': phone.get('id'),  # THIS IS REQUIRED!
                'customer': {
                    'number': '+13529368152'
                }
            }
        )
        
        print(f"\nCall Status: {call_response.status_code}")
        print(f"Response: {call_response.text}")
        
        if call_response.status_code in [200, 201]:
            data = call_response.json()
            print(f"\n✅ SUCCESS! Call initiated!")
            print(f"Call ID: {data.get('id')}")
        else:
            print(f"\n❌ Call failed")
    else:
        print("No phone numbers configured!")
else:
    print(f"Error: {r.text}")
