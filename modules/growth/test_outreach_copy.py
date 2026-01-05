import sys
import os
import io

# utf-8 guard
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.sovereign_dispatch import dispatcher

# User Details
USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

# Copy for "Tardiness"
PAIN_POINT = "Tardiness"
HOOK = "I saw your 1-star review about 'late techs'. Fix it today?"
ANGLE = "Our AI Dispatcher texts customers instantly when techs are late, saving the relationship."
LINK = "https://empire-sovereign-cloud.vercel.app"

def send_sample_outreach():
    print(f"[SAMPLE] Sending '{PAIN_POINT}' Outreach Sample to User...")

    # 1. SMS
    sms_body = f"{HOOK} {ANGLE} Link: {LINK}"
    print(f"   -> SMS Body: {sms_body}")
    
    sms_success = dispatcher.send_sms(
        to_phone=USER_PHONE,
        body=sms_body,
        provider="ghl"
    )

    # 2. Email
    email_subject = f"Question about your 'late techs' review"
    email_body = f"""
    <h2>{HOOK}</h2>
    <p>{ANGLE}</p>
    <p><strong><a href="{LINK}">See it in action here</a></strong></p>
    <br>
    <small>Sent via GHL Sovereign Bridge</small>
    """
    print(f"   -> Email Subject: {email_subject}")

    email_success = dispatcher.send_email(
        to_email=USER_EMAIL,
        subject=email_subject,
        html_body=email_body,
        provider="ghl"
    )

    if sms_success and email_success:
        print("[SUCCESS] Sample Outreach Sent (SMS + Email).")
    else:
        print("[FAIL] One or more channels failed.")

if __name__ == "__main__":
    send_sample_outreach()
