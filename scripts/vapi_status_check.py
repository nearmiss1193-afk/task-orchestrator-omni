import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

def check_vapi_state():
    if not VAPI_API_KEY:
        print("❌ VAPI_PRIVATE_KEY missing from .env")
        return

    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    
    print(f"🔍 Querying Vapi Cloud for Sarah ({ASSISTANT_ID})...")
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print("\n🤖 VAPI ASSISTANT STATUS")
        print("=" * 40)
        print(f"Name:       {data.get('name')}")
        print(f"ServerUrl:  {data.get('serverUrl', '🔴 NOT SET')}")
        print(f"Model:      {data.get('model', {}).get('model')}")
        print(f"Provider:   {data.get('model', {}).get('provider')}")
        
        # Check for static prompt vs dynamic
        messages = data.get('model', {}).get('messages', [])
        current_prompt = messages[0].get('content', '') if messages else ''
        print(f"Prompt Len: {len(current_prompt)} chars")
        
        if data.get('serverUrl'):
            print("✅ LINKED: Vapi is configured to call your Webhook.")
        else:
            print("⚠️ DISCONNECTED: Vapi is using its internal prompt only.")
        print("=" * 40)
    else:
        print(f"❌ API Error: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    check_vapi_state()
