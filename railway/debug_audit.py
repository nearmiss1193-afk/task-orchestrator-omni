
import requests
import json
import time

ENDPOINT = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms"
TEST_PHONE = "+13529368152"

payload = {
    "contactId": "c086f2ce-72f5-4f9f-b414-e0432908c6bc",
    "phone": TEST_PHONE,
    "body": f"Debug Test {int(time.time())}",
    "direction": "inbound",
    "messageId": f"debug_{int(time.time())}",
    "type": "SMS"
}

import time
payload["body"] = f"Debug Test {int(time.time())}"
payload["messageId"] = f"debug_{int(time.time())}"

r = requests.post(ENDPOINT, json=payload, timeout=20)
if r.ok:
    data = r.json()
    print("--- DEBUG LOG ---")
    for line in data.get("debug", []):
        print(line)
else:
    print(f"Error: {r.status_code}")
    print(r.text)
