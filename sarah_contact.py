
from modules.communication.sovereign_dispatch import dispatcher
import time

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

print("=== SARAH THE SPARTAN: FULL CONTACT ===")
print("   Commander, this is Sarah. Initiating multi-channel contact.")

# 1. SMS via GHL (Verified Working)
print("\n[1/3] SMS from Sarah...")
msg = "Hi Commander, Sarah here from AI Service Co. Just confirming our system is fully operational. All channels are GREEN. - Sarah the Spartan"
result = dispatcher.send_sms(USER_PHONE, msg, provider="ghl")
print(f"   SMS: {'SENT' if result else 'FAILED'}")

time.sleep(2)

# 2. Email via GHL
print("\n[2/3] Email from Sarah...")
email_body = """
<div style="font-family: Arial, sans-serif; max-width: 600px;">
    <h2 style="color: #2563eb;">System Status: FULLY OPERATIONAL</h2>
    <p>Commander,</p>
    <p>All communication channels have been verified:</p>
    <ul>
        <li>✅ <strong>SMS</strong> - Working via GHL</li>
        <li>✅ <strong>Voice Calls</strong> - Working via Vapi</li>
        <li>✅ <strong>Email</strong> - You're reading this!</li>
    </ul>
    <p>The Empire is ready for deployment.</p>
    <p style="margin-top: 30px;">
        <em>Sarah the Spartan</em><br>
        Lead Sales Consultant<br>
        AI Service Co.
    </p>
</div>
"""
result = dispatcher.send_email(USER_EMAIL, "Empire Status: All Systems GREEN", email_body, provider="ghl")
print(f"   Email: {'SENT' if result else 'FAILED'}")

time.sleep(2)

# 3. Voice Call via Vapi (Sales Specialist - verified working)
print("\n[3/3] Call from Sarah...")
result = dispatcher.make_call(USER_PHONE)
print(f"   Call: {'INITIATED' if result else 'FAILED'}")

print("\n=== SARAH HAS MADE CONTACT ===")
print("Check your phone for: SMS, Email, and Incoming Call.")
