
import os
import requests
from modules.communications.reliable_email import RESEND_API_KEY

WEBHOOK_URL = "https://empire-unified-backup-production.up.railway.app/resend/webhook"

print(f"Setting up webhook for {WEBHOOK_URL}...")

headers = {
    "Authorization": f"Bearer {RESEND_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "name": "Empire Tracking",
    "endpoint": WEBHOOK_URL,
    "events": [
        "email.sent",
        "email.delivered",
        "email.delivery_delayed",
        "email.bounced",
        "email.complained",
        "email.opened",
        "email.clicked"
    ]
}

try:
    r = requests.post("https://api.resend.com/webhooks", json=payload, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
