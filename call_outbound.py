#!/usr/bin/env python3
"""
OUTBOUND CALL SCRIPT - Uses assistantOverrides to tell Sarah this is OUTBOUND
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID')
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

def call_outbound(phone: str, company: str = "your company", contact_name: str = "there"):
    """Make an outbound call with proper context so Sarah knows it's outbound."""
    
    print(f"📞 Outbound call to {phone} ({contact_name} at {company})...")
    
    # Override Sarah's first message for outbound context
    outbound_first_message = f"""Hi {contact_name}, this is Sarah from AI Service Company. 
I'm following up on the free HVAC business diagnostic we offered. 
I have some insights about {company} that I'd love to share with you. 
Do you have a quick minute?"""
    
    payload = {
        "assistantId": SARAH_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {
            "number": phone,
            "name": contact_name
        },
        # Override for outbound context
        "assistantOverrides": {
            "firstMessage": outbound_first_message,
            "metadata": {
                "call_direction": "outbound",
                "company": company,
                "contact_name": contact_name
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post('https://api.vapi.ai/call/phone', headers=headers, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:200]}")
        if res.status_code in [200, 201]:
            print("✅ OUTBOUND call dispatched - Sarah knows this is outbound!")
            return True
        else:
            print(f"❌ Failed: {res.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python call_outbound.py +1XXXXXXXXXX [company] [contact_name]")
        sys.exit(1)
    
    phone = sys.argv[1]
    company = sys.argv[2] if len(sys.argv) > 2 else "your company"
    contact_name = sys.argv[3] if len(sys.argv) > 3 else "there"
    
    call_outbound(phone, company, contact_name)
