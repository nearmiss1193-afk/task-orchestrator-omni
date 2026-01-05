
import sys
import os

# Add root to pass
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.communication.sovereign_dispatch import dispatcher

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("🚀 Initiating Final Manual Verification Dispatch...")

# 1. Send SMS
sms_body = "COMMANDER: This is the Final Verification Test. If you read this, the Sovereign Dispatch is fully operational. - Spartan AI"
print(f"   📨 Sending SMS to {USER_PHONE}...")
sms_success = dispatcher.send_sms(USER_PHONE, sms_body, provider="ghl")
print(f"   SMS Result: {sms_success}")

# 2. Send Email
email_body = """
<h3>Sovereign Dispatch Verification</h3>
<p>Commander,</p>
<p>This email confirms that the Empire Unified communication bridge is active.</p>
<p><b>Status:</b> ONLINE<br>
<b>Agent:</b> Spartan V3<br>
<b>Protocol:</b> Sovereign</p>
<p>End of Line.</p>
"""
print(f"   📧 Sending Email to {USER_EMAIL}...")
email_success = dispatcher.send_email(
    to_email=USER_EMAIL, 
    subject="Final System Verification: SUCCESS", 
    html_body=email_body, 
    provider="ghl"
)
print(f"   Email Result: {email_success}")

if sms_success and email_success:
    print("✅ ALL SYSTEMS GO.")
else:
    print("⚠️ PARTIAL FAILURE.")
