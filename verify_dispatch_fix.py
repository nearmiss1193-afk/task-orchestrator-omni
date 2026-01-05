
from modules.communication.sovereign_dispatch import dispatcher
import os

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("🔍 Starting Dispatch Verification...")

# 1. Test SMS
print(f"📱 Sending Test SMS to {USER_PHONE}...")
sms_ok = dispatcher.send_sms(USER_PHONE, "COMMANDER: Omni-Router Fix Verified. Inbound logic is now using ContactID directly.", provider="ghl")
print(f"   SMS Status: {'✅ SENT' if sms_ok else '❌ FAILED'}")

# 2. Test Email
print(f"📧 Sending Test Email to {USER_EMAIL}...")
email_body = """
<h1>Omni-Router Status: ONLINE</h1>
<p>Commander,</p>
<p>The logic conflict (Phone vs ContactID) has been resolved.</p>
<p>The Inbound Poller is being restarted now. It will reply to incoming texts immediately.</p>
<p><b>Status:</b> GREEN</p>
"""
email_ok = dispatcher.send_email(
    USER_EMAIL, 
    "Omni-Router Verification", 
    email_body, # Correct arg
    provider="ghl"
)
print(f"   Email Status: {'✅ SENT' if email_ok else '❌ FAILED'}")
