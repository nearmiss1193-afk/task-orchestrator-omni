"""Test Sarah SMS response on the practice number via Railway"""
import requests
import json
import time

# Live Railway Endpoint
ENDPOINT = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms"

# Practice number the user provided
PRACTICE_PHONE = "+18639465043"  # +1 863-946-5043

def test_sarah_response():
    print(f"[TEST] Testing Sarah SMS Response")
    print(f"[TEST] Endpoint: {ENDPOINT}")
    print(f"[TEST] Practice Phone: {PRACTICE_PHONE}")
    
    unique_id = int(time.time())
    
    # Payload mimicking what GHL Workflow A would send
    payload = {
        "contactId": f"practice_test_{unique_id}",
        "phone": PRACTICE_PHONE,
        "body": "Hi, I'm interested in your AI phone service. Can you tell me more?",
        "direction": "inbound",
        "messageId": f"practice_msg_{unique_id}",
        "type": "SMS"
    }
    
    print(f"\n[TEST] Sending Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        start_time = time.time()
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        duration = time.time() - start_time
        
        print(f"\n[TEST] Response {response.status_code} in {duration:.2f}s")
        print(f"[TEST] Body: {response.text}")
        
        if response.ok:
            data = response.json()
            if data.get("reply_sent"):
                print("\n[SUCCESS] Sarah generated and sent a reply!")
                print(f"[SUCCESS] Reply Method: Workflow B")
                print("[NEXT] Check GHL Conversations for the practice number to see the reply.")
            elif data.get("status") == "skipped":
                print(f"\n[SKIPPED] Reason: {data.get('reason')}")
                if "duplicate" in str(data.get("reason", "")):
                    print("[INFO] This message was already processed. Try with a different message.")
            else:
                print(f"\n[WARNING] Reply NOT sent. Check debug log:")
                print(data.get("debug", []))
        else:
            print(f"\n[ERROR] Server returned error: {response.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")

if __name__ == "__main__":
    test_sarah_response()
