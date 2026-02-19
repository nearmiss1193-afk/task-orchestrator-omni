"""Test sending SMS via Vapi phone number to Dan"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

# Vapi can send SMS through our numbers
# Sarah's number: +18632132505
# Let's check if Vapi supports sending SMS

# First get our phone numbers
r = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {key}"})
nums = r.json()
for n in nums:
    print(f"  {n.get('name','')} | {n.get('number','')} | id: {n.get('id','')}")

# Check Resend API key
resend_key = os.environ.get("RESEND_API_KEY", "")
print(f"\nResend key available: {bool(resend_key)}")

if resend_key:
    # Send email notification to Dan
    r2 = requests.post("https://api.resend.com/emails", headers={
        "Authorization": f"Bearer {resend_key}",
        "Content-Type": "application/json"
    }, json={
        "from": "Sarah AI <owner@aiserviceco.com>",
        "to": ["dan@aiserviceco.com"],
        "subject": "📞 CALL ALERT: Someone called Sarah!",
        "text": "TEST: This is a notification test. If you see this email, notifications via Resend work.\n\nCall alerts will be sent to this email after every call to Sarah."
    })
    print(f"Resend email test: {r2.status_code} - {r2.text[:200]}")
