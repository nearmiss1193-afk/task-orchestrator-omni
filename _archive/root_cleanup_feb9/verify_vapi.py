
import os
import requests

def verify_vapi():
    api_key = os.environ.get("VAPI_PRIVATE_KEY")
    if not api_key:
        print("❌ Error: VAPI_PRIVATE_KEY missing")
        return

    print("📡 VERIFY: Checking Vapi API Status...")
    url = "https://api.vapi.ai/assistant"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            assistants = response.json()
            print(f"✅ Vapi Connection OK. Found {len(assistants)} assistants.")
            # Note: Checking "funding" isn't direct via API, but key working is Phase A.
            return True
        else:
            print(f"❌ Vapi Connection Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Vapi Verification Failed: {e}")
        return False

if __name__ == "__main__":
    verify_vapi()
