import requests
import json
import time

# Workflow B Webhook URL (from app.py)
WEBHOOK_URL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/44e67279-2ad5-491c-82f0-f8eaadea085c"

def test_workflow_b():
    print(f"[TEST] Testing Workflow B Webhook: {WEBHOOK_URL}...")
    
    payload = {
        "phone": "+13529368152",  # User's backup phone (from app.py)
        "replyText": "Test message from Antigravity verification script.",
        "sourceMessageId": f"test-{int(time.time())}"
    }
    
    print(f"[TEST] Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        duration = time.time() - start_time
        
        print(f"[TEST] Status Code: {response.status_code}")
        print(f"[TEST] Response Body: {response.text}")
        print(f"[TEST] Duration: {duration:.2f}s")
        
        if response.ok:
            print("[TEST] ✅ SUCCESS: Webhook accepted the request.")
            print("[TEST] NOTE: This only confirms the webhook is reachable. Check your phone (+13529368152) to see if the SMS arrived.")
        else:
            print("[TEST] ❌ FAILED: Webhook rejected the request.")
            
    except Exception as e:
        print(f"[TEST] ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_workflow_b()
