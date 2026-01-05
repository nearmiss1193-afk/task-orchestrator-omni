
from modules.communication.sovereign_dispatch import dispatcher
import time

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("=== FINAL COMMS TEST (All Channels) ===")

# 1. SMS via TWILIO DIRECT (This WORKED before)
print("\n[1/3] SMS via Twilio Direct...")
msg = "Sarah here. Final System Test. Reply 'CONFIRMED' if you get this."
result = dispatcher.send_sms(USER_PHONE, msg, provider="twilio")
print(f"   Result: {'OK' if result else 'FAIL'}")

time.sleep(2)

# 2. Email via RESEND Direct
print("\n[2/3] Email via Resend...")
email_body = """
<h2>Empire System Online</h2>
<p>This is a direct Resend test. If you see this, email channel is GREEN.</p>
<p>- Sovereign AI</p>
"""
result = dispatcher.send_email(USER_EMAIL, "Empire Final Test 2/3", email_body, provider="resend")
print(f"   Result: {'OK' if result else 'FAIL'}")

time.sleep(2)

# 3. Voice Call via Vapi
print("\n[3/3] Call via Vapi...")
result = dispatcher.make_call(USER_PHONE)
print(f"   Result: {'OK' if result else 'FAIL'}")

print("\n=== TEST COMPLETE ===")
print("Check your phone for: SMS, Email (Inbox/Spam), and Incoming Call.")
