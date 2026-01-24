
import requests
import json
import time

# URL found from previous context
WEBHOOK_URL = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"

payload = {
    "type": "CallStatus",
    "status": "no-answer",
    "contact_id": "verify_test_001",
    "contact": {
        "id": "verify_test_001",
        "name": "Verification Bot",
        "phone": "+15550000000"
    },
    "direction": "inbound"
}

print(f"🚀 Simulating Missed Call to: {WEBHOOK_URL}")
try:
    res = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"❌ Error: {e}")
