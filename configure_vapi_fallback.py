"""
configure_vapi_fallback.py
==========================
Configures Vapi assistant to forward calls to a fallback phone number
when the AI doesn't pick up.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY") or os.getenv("VAPI_API_KEY")
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
FALLBACK_PHONE = "+13529368152"  # User's cell phone

def configure_fallback():
    """Configure Sarah assistant to forward to fallback phone on no answer."""
    
    if not VAPI_API_KEY:
        print("❌ VAPI_API_KEY not found in .env")
        return False
    
    url = f"https://api.vapi.ai/assistant/{SARAH_ASSISTANT_ID}"
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Configure forwarding settings
    payload = {
        "forwardingPhoneNumber": FALLBACK_PHONE,
        "forwardingTimeoutSeconds": 30,  # Wait 30 seconds before forwarding
        "voicemailDetectionConfig": {
            "enabled": True,
            "provider": "twilio"
        }
    }
    
    try:
        # First, get current config
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            current = response.json()
            print(f"✅ Current assistant: {current.get('name')}")
            print(f"📞 Current forwarding: {current.get('forwardingPhoneNumber', 'None')}")
        
        # Update with fallback
        response = requests.patch(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ Fallback configured: {updated.get('forwardingPhoneNumber')}")
            print(f"⏱️ Timeout: {updated.get('forwardingTimeoutSeconds', 30)}s")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📞 Configuring Vapi Call Forwarding...")
    print(f"   Fallback Number: {FALLBACK_PHONE}")
    print("=" * 50)
    configure_fallback()
