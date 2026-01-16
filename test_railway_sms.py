import requests
import json

url = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms"
payload = {
    "phone": "+18638129362",
    "message": "Hi Sarah, can you tell me more about the audit you sent?",
    "contactId": "test_manus_manual",
    "messageId": "msg_manus_manual"
}

print(f"Testing Railway endpoint: {url}")
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
