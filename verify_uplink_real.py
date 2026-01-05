
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# PRODUCTION URL (The one the User uses)
CLOUD_URL = "https://empire-sovereign-cloud.vercel.app/api/chat"
# Local Agent should be polling the DB now.

def test_live_uplink():
    print("🚀 PROBING CLOUD UPLINK...")
    
    payload = {"command": "status check (RCA Verification)"}
    
    try:
        # 1. Send Command to Cloud
        print(f"   -> POST {CLOUD_URL}")
        start = time.time()
        res = requests.post(CLOUD_URL, json=payload, timeout=10)
        latency = (time.time() - start) * 1000
        
        print(f"   <- RESPONSE: {res.status_code} ({latency:.0f}ms)")
        print(f"   <- BODY: {res.json()}")
        
        if res.status_code == 200 and "Sent to Core" in res.json().get('response', ''):
            print("✅ STEP 1 PASS: Cloud accepted command into DB.")
        else:
            print("❌ STEP 1 FAIL: Cloud did not queue command.")
            return

        print("\n⏳ WAITING FOR LOCAL BRIDGE TO EXECUTE...")
        print("   (Watch your local 'uplink_bridge' terminal for output)")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    test_live_uplink()
