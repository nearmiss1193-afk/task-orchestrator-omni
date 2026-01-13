import requests
import json
import time

URL = "https://empire-unified-backup-production.up.railway.app/vapi/webhook"

def simulate_call():
    print(f"Testing Vapi Webhook at: {URL}")
    
    # 1. Simulate Incoming Call (Assistant Request)
    payload_setup = {
        "message": {
            "type": "assistant-request",
            "call": {"customer": {"number": "+15550199999"}}
        }
    }
    try:
        r = requests.post(URL, json=payload_setup, timeout=10)
        print(f"Setup Response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Setup Failed: {e}")

    # 2. Simulate Missed Call (Should trigger SMS logic)
    payload_missed = {
        "message": {
            "type": "end-of-call-report",
            "endedReason": "no-answer",
            "call": {
                "customer": {"number": "+15550199999", "name": "Test Prospect"}
            }
        }
    }
    try:
        r = requests.post(URL, json=payload_missed, timeout=10)
        print(f"Missed Call Response: {r.status_code} - {r.text}")
        if r.ok:
            print("✅ Webhook processed successfully. (Check Backup Phone for SMS if configured)")
    except Exception as e:
        print(f"Missed Call Failed: {e}")

if __name__ == "__main__":
    simulate_call()
