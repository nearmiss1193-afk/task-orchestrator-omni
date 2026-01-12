"""
FIX VAPI CALL DIRECTION - Create separate modes for inbound/outbound
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

def get_phone_numbers():
    """Get all phone numbers from Vapi"""
    print("=== VAPI PHONE NUMBERS ===")
    resp = requests.get(
        "https://api.vapi.ai/phone-number",
        headers={"Authorization": f"Bearer {VAPI_KEY}"}
    )
    if resp.status_code == 200:
        phones = resp.json()
        for p in phones:
            print(f"  ID: {p.get('id')}")
            print(f"  Number: {p.get('number')}")
            print(f"  Provider: {p.get('provider')}")
            print(f"  Assistant: {p.get('assistantId', 'NOT SET')}")
            print()
        return phones
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
        return []

def get_assistant(assistant_id):
    """Get assistant details"""
    print(f"=== ASSISTANT: {assistant_id} ===")
    resp = requests.get(
        f"https://api.vapi.ai/assistant/{assistant_id}",
        headers={"Authorization": f"Bearer {VAPI_KEY}"}
    )
    if resp.status_code == 200:
        asst = resp.json()
        print(f"  Name: {asst.get('name')}")
        print(f"  First Message: {asst.get('firstMessage', 'N/A')[:100]}...")
        return asst
    else:
        print(f"Error: {resp.status_code}")
        return None

def main():
    print("="*60)
    print("VAPI CONFIGURATION CHECK")
    print("="*60)
    print()
    print(f"ENV VAPI_PHONE_NUMBER_ID: {VAPI_PHONE_ID}")
    print()
    
    phones = get_phone_numbers()
    print()
    
    # Check if our configured phone ID is valid
    valid_ids = [p.get('id') for p in phones]
    if VAPI_PHONE_ID and VAPI_PHONE_ID not in valid_ids:
        print(f"!!! WARNING: VAPI_PHONE_NUMBER_ID '{VAPI_PHONE_ID}' NOT FOUND IN VAPI !!!")
        print(f"Valid IDs: {valid_ids}")
    
    # Get Sarah assistant
    get_assistant(SARAH_ASSISTANT_ID)
    
    print()
    print("="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print("To fix inbound/outbound confusion, Sarah's system prompt should include:")
    print('  "If the customer initiated this call (inbound), greet them as a receptionist."')
    print('  "If you initiated this call (outbound), introduce yourself as calling them."')
    print()
    print("Vapi provides call.direction in metadata - we can use this!")

if __name__ == "__main__":
    main()
