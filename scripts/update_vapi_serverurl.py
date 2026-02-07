"""Update Vapi Sarah assistant serverUrl to new Modal endpoint"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah the Spartan
NEW_SERVER_URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

def update_server_url():
    if not VAPI_API_KEY:
        print("❌ VAPI_PRIVATE_KEY not found in .env")
        return False
    
    print(f"🔑 Using Vapi key: {VAPI_API_KEY[:10]}...")
    print(f"🤖 Updating assistant: {ASSISTANT_ID}")
    print(f"🔗 New serverUrl: {NEW_SERVER_URL}")
    
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, get current assistant
    get_response = requests.get(url, headers=headers)
    if get_response.status_code != 200:
        print(f"❌ Failed to get assistant: {get_response.status_code}")
        print(get_response.text)
        return False
    
    current = get_response.json()
    print(f"✅ Found assistant: {current.get('name')}")
    print(f"   Current serverUrl: {current.get('serverUrl', 'NOT SET')}")
    
    # Update serverUrl
    payload = {
        "serverUrl": NEW_SERVER_URL
    }
    
    patch_response = requests.patch(url, headers=headers, json=payload)
    
    if patch_response.status_code == 200:
        updated = patch_response.json()
        print(f"✅ serverUrl updated successfully!")
        print(f"   New serverUrl: {updated.get('serverUrl')}")
        return True
    else:
        print(f"❌ Failed to update: {patch_response.status_code}")
        print(patch_response.text)
        return False

if __name__ == "__main__":
    update_server_url()
