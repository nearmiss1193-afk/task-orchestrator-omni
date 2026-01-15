import requests
import json
import time

# Live Railway Endpoint
ENDPOINT = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms"

# User's verified testing number (from app.py)
TEST_PHONE = "+13529368152"

def simulate_inbound_sms():
    print(f"[DEBUG] Simulating GHL Inbound SMS to: {ENDPOINT}")
    
    # Payload mimicking what GHL Workflow A sends
    payload = {
        "contactId": "test_contact_debug_001",
        "phone": TEST_PHONE,
        "body": "Hello Sarah, are you there? This is a debug test.",
        "direction": "inbound",
        "messageId": f"debug_msg_{int(time.time())}",
        "type": "SMS"
    }
    
    print(f"[DEBUG] Sending Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(ENDPOINT, json=payload, timeout=20)
        duration = time.time() - start_time
        
        print(f"[DEBUG] Response {response.status_code} in {duration:.2f}s")
        print(f"[DEBUG] Body: {response.text}")
        
        if response.ok:
            data = response.json()
            if data.get("reply_sent"):
                print("[DEBUG] ✅ SUCCESS: Railway processed message and sent reply to Workflow B.")
                print(f"[DEBUG] Reply Method: {data.get('method')}")
                print("[ANALYSIS] If you received this SMS, the issue is UPSTREAM (GHL Workflow A not triggering).")
                print("[ANALYSIS] If you did NOT receive this SMS, the issue is DOWNSTREAM (Workflow B configuration).")
            else:
                print("[DEBUG] ⚠️ RECEIVED but NO REPLY sent.")
                print(f"[DEBUG] Reason: {data.get('reason')}")
        else:
            print("[DEBUG] ❌ FAILED: Server returned error.")
            
    except Exception as e:
        print(f"[DEBUG] ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    simulate_inbound_sms()
