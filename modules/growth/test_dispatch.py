import os
import requests
import sys
from dotenv import load_dotenv
from twilio.rest import Client

env_path = os.path.join(os.getcwd(), '.env')
load_dotenv(env_path)

def send_test_dispatch():
    print("🚀 Initiating SOVEREIGN DISPATCH (No-GHL)...")
    
    # User Details
    target_email = "nearmiss1193@gmail.com"
    
    # Config
    resend_key = os.environ.get("RESEND_API_KEY")
    
    if not resend_key:
        print("❌ ERROR: Missing RESEND_API_KEY in .env")
        return

    # Content
    link = "https://empire-sovereign-cloud.vercel.app"
    email_subject = "Fixing the 'Tardiness' reviews for Iceberg HVAC"
    email_body = f"""
    <p>Saw the 1-star review about 'late techs'.</p>
    <p>My AI can text clients instantly when techs are late, saving the relationship.</p>
    <p><strong>Want a demo?</strong></p>
    <p><a href="{link}">See it here: {link}</a></p>
    """

    # 1. Send Email via Resend
    print(f"   📧 Sending Email via Resend to {target_email}...")
    
    headers = {
        'Authorization': f'Bearer {resend_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "from": "Sovereign AI <onboarding@resend.dev>",
        "to": [target_email],
        "subject": email_subject,
        "html": email_body
    }
    
    try:
        res = requests.post("https://api.resend.com/emails", json=payload, headers=headers)
        if res.status_code in [200, 201]:
            print(f"   ✅ EMAIL SENT! ID: {res.json().get('id')}")
        else:
            print(f"   ⚠️ Email Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"   ❌ Email Exception: {e}")

    # 2. SMS via Twilio
    print("\n   📱 Sending SMS via Twilio...")
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    twilio_from = os.environ.get("TWILIO_FROM_NUMBER", "").strip()
    
    if twilio_sid and not twilio_sid.startswith("AC"):
        print(f"❌ CONFIG ERROR: TWILIO_ACCOUNT_SID must start with 'AC'. Found: '{twilio_sid[:2]}...'")
        print("   -> Please get the 'Account SID' from the main Twilio Dashboard.")
        return
    
    if twilio_sid:
        print(f"      SID Loaded: {twilio_sid[:4]}...{twilio_sid[-4:]}")
    if twilio_token:
        print(f"      Token Loaded: {twilio_token[:4]}...{twilio_token[-4:]}")

    sms_body = f"Saw the review about early/late techs. AI Dispatcher fixes this instantly. Demo: {link}"

    if twilio_sid and twilio_token and twilio_from:
        try:
            client = Client(twilio_sid, twilio_token)
            message = client.messages.create(
                body=sms_body,
                from_=twilio_from,
                to="+13529368152"
            )
            print(f"   ✅ SMS SENT! SID: {message.sid}")
        except Exception as e:
            print(f"   ❌ SMS Failed: {e}")
    else:
        print("   ⚠️ Missing Twilio Config in .env")

if __name__ == "__main__":
    send_test_dispatch()
