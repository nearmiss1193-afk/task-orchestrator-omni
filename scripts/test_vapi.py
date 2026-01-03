import os
import requests
import json

# --- CONFIG ---
# Taking key from deploy.py knowledge
VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY") or "c23c884d-0008-4b14-ad5d-530e98d0c9da"

def test_vapi_connection():
    print("🎙️ TESTING VAPI CONNECTION...")
    
    headers = {
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. List Assistants
    try:
        url = "https://api.vapi.ai/assistant"
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            assistants = res.json()
            print(f"FOUND {len(assistants)} ASSISTANTS")
            for a in assistants:
                print(f"NAME: {a.get('name')} | ID: {a.get('id')}")
            return assistants
        else:
            print(f"❌ Vapi Connect Failed: {res.status_code} - {res.text}")
            return []
            
    except Exception as e:
        print(f"❌ Vapi Error: {e}")
        return []

if __name__ == "__main__":
    test_vapi_connection()
