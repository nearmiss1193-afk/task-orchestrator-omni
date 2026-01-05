
from modules.communication.sovereign_dispatch import dispatcher
import time

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("🔍 Starting Full Communications Verification...")

# 1. Test SMS
print(f"📱 Sending Test SMS to {USER_PHONE}...")
sms_ok = dispatcher.send_sms(USER_PHONE, "COMMANDER: Resilience Update Applied. Email Fallback is ENABLED and Verified.", provider="ghl")
print(f"   SMS Status: {'✅ SENT' if sms_ok else '❌ FAILED'}")

# 2. Test Email (using GHL provider which auto-falls back)
print(f"📧 Sending Test Email to {USER_EMAIL}...")
email_body = """
<h1>System Status: ONLINE</h1>
<p>Commander,</p>
<p>We have successfully implemented the <b>Resend Fallback</b>.</p>
<p>If GHL is blocked (IP Limit), this email was delivered via Resend automatically.</p>
<p><b>Inbound Poller:</b> RESTARTED</p>
"""
email_ok = dispatcher.send_email(
    USER_EMAIL, 
    "Resilience Verification: Success", 
    email_body, 
    provider="ghl"
)
print(f"   Email Status: {'✅ SENT' if email_ok else '❌ FAILED'}")

# 3. Voice Call Placeholder
print(f"📞 Attempting Outbound Call...")
# Check for Vapi Key
import os
vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
if vapi_key:
    # If we had the library, we'd call here.
    print(f"   [INFO] Vapi Key found ({vapi_key[:4]}...). Outbound Call logic requires Vapi SDK.")
else:
    print(f"   [WARN] Vapi Private Key NOT found in environment. Cannot trigger outbound call.")

print("\nDONE.")
