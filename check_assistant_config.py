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

def check_config():
    # Get Assistant ID from file or search
    assistant_id = "033ec1d3-e17d-4611-a497-b47cab1fdb4e" # Office Manager
    
    print(f"🔍 Checking Configuration for Assistant: {assistant_id}")
    res = requests.get(f"https://api.vapi.ai/assistant/{assistant_id}", headers=HEADERS)
    
    if res.status_code == 200:
        data = res.json()
        print(f"✅ Assistant Found: {data.get('name')}")
        print(f"   - Model: {data.get('model', {}).get('model')}")
        print(f"   - First Message: {data.get('firstMessage')}")
        print(f"   - Voice: {data.get('voice', {}).get('voiceId')}")
        print(f"   - Server URL: {data.get('serverUrl')}")
        
        if not data.get('firstMessage'):
             print("⚠️ WARNING: No First Message set! The bot might be silent.")
             
        # Check Phone Numbers linked to this assistant
        print("\n🔍 Checking Linked Phone Numbers...")
        p_res = requests.get("https://api.vapi.ai/phone-number", headers=HEADERS)
        if p_res.status_code == 200:
            numbers = p_res.json()
            linked_nums = [n.get('number') for n in numbers if n.get('assistantId') == assistant_id]
            if linked_nums:
                print(f"✅ Active Numbers: {linked_nums}")
            else:
                print("❌ NO PHONE NUMBERS LINKED TO ASSISTANT!")
        else:
            print(f"❌ Failed to fetch numbers: {p_res.status_code}")
            
    else:
        print(f"❌ Failed to fetch assistant: {res.text}")

if __name__ == "__main__":
    check_config()
