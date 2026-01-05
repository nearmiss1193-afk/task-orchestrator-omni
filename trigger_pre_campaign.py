
from modules.communication.sovereign_dispatch import dispatcher
import time

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("⚔️ STARTING PRE-CAMPAIGN BATTLE TEST ⚔️")
print("   Target: Commander (Sarah's Boss)")

# 1. SMS
msg = "Hi, it's Sarah. Verification Test: 1 of 3 (SMS). Reply 'GO' if you get this."
print(f"\n📱 1. Sending SMS...")
success = dispatcher.send_sms(USER_PHONE, msg, provider="ghl")
if not success:
    print("   [FALLBACK] GHL failed/skipped, trying Twilio direct...")
    dispatcher.send_sms(USER_PHONE, msg, provider="twilio")

time.sleep(2)

# 2. Email
print(f"\n📧 2. Sending Email...")
email_body = """
<h3>Verification Test: 2 of 3 (Email)</h3>
<p>System is <b>ONLINE</b>.</p>
<p>If you are reading this, the Resend/GHL uplink is secure.</p>
<p>- Sarah the Spartan</p>
"""
# FORCE RESEND (Skip GHL for now to ensure delivery)
dispatcher.send_email(USER_EMAIL, "Empire Verification: 2/3", email_body, provider="resend")

time.sleep(2)

# 3. Phone Call
print(f"\n📞 3. Initiating Voice Call...")
# Explicitly pass the ID we found, just in case
dispatcher.make_call(USER_PHONE, assistant_id="8a7f18bf-8c1e-4eaf-afdd-7a8339f40079")

print("\n✅ TEST SEQUENCE COMPLETE.")
