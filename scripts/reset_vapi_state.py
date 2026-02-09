import os
import requests
import time
from dotenv import load_dotenv

load_dotenv() # Load from .env 
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY") or os.getenv("VAPI_API_KEY")
print(f"🔑 Debug: VAPI_API_KEY length: {len(VAPI_API_KEY) if VAPI_API_KEY else 'MISSING'}")
if VAPI_API_KEY:
    print(f"🔑 Debug: VAPI_API_KEY prefix: {VAPI_API_KEY[:5]}...")

ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah
MODAL_URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"
DUMMY_URL = "https://google.com/temp-refresh"

def force_refresh():
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"

    print(f"🔄 Phase 1: Patching to DUMMY URL to invalidate cache...")
    resp1 = requests.patch(url, headers=headers, json={"serverUrl": DUMMY_URL})
    if resp1.status_code == 200:
        print("✅ Success. Waiting 5 seconds for Vapi propagation...")
        time.sleep(5)
    else:
        print(f"❌ Failed Phase 1: {resp1.text}")
        return

    print(f"🔄 Phase 2: Restoring PRODUCTION Modal URL...")
    resp2 = requests.patch(url, headers=headers, json={"serverUrl": MODAL_URL})
    if resp2.status_code == 200:
        print("✅ Success. Vapi cloud state should be refreshed.")
    else:
        print(f"❌ Failed Phase 2: {resp2.text}")

if __name__ == "__main__":
    force_refresh()
