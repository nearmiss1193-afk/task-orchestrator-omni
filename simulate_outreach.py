
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e" # +18632132505

MODAL_BASE_URL = "https://nearmiss1193-afk--nexus-outreach-v1"
GHL_WEBHOOK_URL = f"{MODAL_BASE_URL}-ghl-webhook.modal.run"
VAPI_WEBHOOK_URL = f"{MODAL_BASE_URL}-vapi-webhook.modal.run"

TARGET_PHONE = "+13529368152"
OWNER_EMAIL = "nearmiss1193@gmail.com"

def send_test_email():
    # Email currently goes via GHL hook in workers/outreach.py
    # For simulation, we'll just check if we can hit the Modal GHL hook with email payload
    print("📧 Simulating Email via Modal GHL Hook...")
    payload = {
        "type": "email_test",
        "email": OWNER_EMAIL,
        "subject": "Turbo Test",
        "body": "Sarah AI Hardening Test"
    }
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload)
        print(f"Modal GHL Status: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def send_test_sms():
    print("📱 Simulating SMS via Modal GHL Hook...")
    payload = {
        "type": "sms_test",
        "phone": TARGET_PHONE,
        "message": "Sarah Hardening Test"
    }
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload)
        print(f"Modal GHL Status: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def trigger_test_call():
    print("⏳ Waiting 10s for Vapi cooling...")
    time.sleep(10)
    print("📞 Triggering Sarah AI test call...")
    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": PHONE_ID,
        "assistantId": SARAH_ID,
        "customer": {
            "number": TARGET_PHONE,
            "name": "Dan"
        },
        "assistant": {
            "firstMessage": "Hey Dan! It's Sarah from AI Service Co. Verification round complete. All systems are officially working."
        }
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"Call Status: {res.status_code}")
        print(res.text)
    except Exception as e:
        print(f"Call Error: {e}")

if __name__ == "__main__":
    send_test_email()
    send_test_sms()
    trigger_test_call()
