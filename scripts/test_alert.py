import os
import sys

# Add modules to path
sys.path.append(os.path.join(os.getcwd(), 'modules'))

try:
    from communications.email_direct import send_email_direct as send_email
    from communications.sms import send_sms
except ImportError:
    print("Could not import communication modules. Ensure you are in the project root.")
    sys.path.append(os.getcwd())
    from modules.communications.email_direct import send_email_direct as send_email
    from modules.communications.sms import send_sms

USER_EMAIL = "owner@aiserviceco.com"
USER_PHONE = "+13529368152"

def test_alerts():
    print(f"Testing Alerts to:\nEmail: {USER_EMAIL}\nPhone: {USER_PHONE}")
    
    # 1. Send Email
    try:
        print("Sending Email...")
        # Mocking or using actual implementation depending on env
        # Assuming send_email(to, subject, body) signature
        result_email = send_email(
            to_email=USER_EMAIL, 
            subject="Empire Alert Test: Booking System", 
            body="This is a test to confirm your Booking Alert channel is valid. If you see this, the Sovereign Stack can reach you."
        )
        print(f"Email Result: {result_email}")
    except Exception as e:
        print(f"Email Failed: {e}")

    # 2. Send SMS
    try:
        print("Sending SMS...")
        result_sms = send_sms(
            to_number=USER_PHONE,
            message="Empire Alert: System Check. Booking Alerts are configured. Confirming reachability."
        )
        print(f"SMS Result: {result_sms}")
    except Exception as e:
        print(f"SMS Failed: {e}")

if __name__ == "__main__":
    test_alerts()
