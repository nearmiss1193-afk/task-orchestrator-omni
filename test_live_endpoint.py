import requests
import json
import time

# Live Railway URL
LIVE_URL = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms"

def test_live_endpoint():
    print(f"[TEST] Testing Live Endpoint: {LIVE_URL}...")
    
    # Payload designed to be "skipped" safely but prove the endpoint exists
    # Missing 'phone' so it should return 400 or "no contact identifier"
    payload = {
        "source": "antigravity_verification",
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(LIVE_URL, json=payload, timeout=10)
        
        print(f"[TEST] Status Code: {response.status_code}")
        print(f"[TEST] Response Body: {response.text}")
        
        if response.status_code == 404:
            print("[TEST] ❌ FAILED: Endpoint not found (404). Deployment might be pending or failed.")
        elif response.status_code == 400 and "no contact identifier" in response.text:
            print("[TEST] ✅ SUCCESS: Endpoint is reachable and processing logic (returned expected 400).")
        elif response.status_code == 200:
            print("[TEST] ✅ SUCCESS: Endpoint is reachable.")
        else:
            print(f"[TEST] ⚠️ INDETERMINATE: Unexpected status {response.status_code}.")

    except Exception as e:
        print(f"[TEST] ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_live_endpoint()
