"""Test: Simulate an end-of-call-report webhook to Modal and see what happens"""
import json
import requests

# The exact URL Vapi should be hitting
webhook_url = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

# Simulate a real end-of-call-report payload
test_payload = {
    "message": {
        "type": "end-of-call-report",
        "call": {
            "id": "test-call-12345",
            "type": "inboundPhoneCall",
            "status": "ended",
            "endedReason": "customer-ended-call",
            "customer": {
                "number": "+13529368152"
            },
            "phoneNumber": {
                "number": "+18632132505"
            }
        },
        "transcript": "AI: Hello, this is Sarah with AI Service Co. How can I help you today?\nUser: Hi, just testing.\nAI: Great! Thanks for calling!",
        "summary": "Test call - customer was just testing the system.",
        "durationSeconds": 15
    }
}

print(f"Sending simulated end-of-call-report to: {webhook_url}")
print(f"Payload phone: +13529368152")

try:
    r = requests.post(webhook_url, json=test_payload, timeout=30)
    print(f"\nStatus: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
