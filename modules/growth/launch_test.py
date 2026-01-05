import sys
import os
import io

# utf-8 guard
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.sovereign_dispatch import dispatcher

# User's Personal Number
TEST_PHONE = "+13526453244" 

def run_launch_test():
    print(f"[LAUNCH] Initiating Launch Test to {TEST_PHONE} via GHL...")
    
    msg = (
        "Sovereign Command: 24/7 Monitoring Active.\n"
        "We are watching SMS, Email, and Socials.\n"
        "Reply 'READY' to confirm receipt."
    )
    
    # Send via GHL SMS
    print("   -> Sending GHL SMS...")
    sms_success = dispatcher.send_sms(
        to_phone=TEST_PHONE,
        body=msg,
        provider="ghl"
    )
    
    # Send via GHL Email
    print("   -> Sending GHL Email...")
    TEST_EMAIL = "nearmiss1193@gmail.com"
    email_success = dispatcher.send_email(
        to_email=TEST_EMAIL,
        subject="Sovereign Launch Verified",
        html_body="<h2>Command Bridge Active</h2><p>GHL is successfully delivering messages.</p>",
        provider="ghl"
    )
    
    if sms_success and email_success:
        print("[SUCCESS] FULL LAUNCH SUCCESS (SMS + Email).")
    elif sms_success or email_success:
        print("[PARTIAL] PARTIAL SUCCESS (One Channel Failed).")
    else:
        print("[FAIL] ALL CHANNELS FAILED.")

if __name__ == "__main__":
    run_launch_test()
