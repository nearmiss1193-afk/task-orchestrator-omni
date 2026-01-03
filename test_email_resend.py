import os
import resend
from dotenv import load_dotenv

# Load Env
load_dotenv()

# manual override for safety if .env didn't load
key = os.getenv("RESEND_API_KEY") or "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"
resend.api_key = key

print(f"📧 Testing Resend with Key: {key[:5]}...{key[-5:]}")

params = {
    "from": "alert@aiserviceco.com",
    "to": ["owner@aiserviceco.com"],
    "subject": "Sovereign Command: Comms Link Restored",
    "html": "<strong>Confirming neural uplink restored.</strong><br>The RESEND_API_KEY has been successfully integrated.<br>System Status: ONLINE."
}

try:
    email = resend.Emails.send(params)
    print("✅ Success! Email Sent.")
    print(email)
except Exception as e:
    print(f"❌ Failed to send: {e}")
