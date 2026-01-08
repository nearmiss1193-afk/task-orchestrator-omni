"""
REFERRAL ENGINE
===============
Automated referral requests after positive calls.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

REFERRAL_SMS = """Hey {name}! Thanks again for choosing us. 🙏

Quick favor: Know anyone who needs {service}? Send them our way and we'll give you BOTH $50 off your next service!

Just have them mention your name when they call. - The {company} Team"""

REFERRAL_EMAIL_SUBJECT = "A quick thank you + a favor 🙏"
REFERRAL_EMAIL_BODY = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<h2>Thanks for choosing {company}!</h2>
<p>Hi {name},</p>
<p>We really appreciate your business. It was great serving you!</p>
<p><strong>Quick favor:</strong> Know any friends, family, or neighbors who might need {service}?</p>
<div style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
<strong>🎁 Referral Reward:</strong><br>
For every person you refer who becomes a customer, you BOTH get <strong>$50 off</strong> your next service!
</div>
<p>Just have them mention your name when they call us at <a href="tel:+18632132505">(863) 213-2505</a>.</p>
<p>Thanks again!<br>The {company} Team</p>
</body>
</html>
"""


def send_referral_request(customer: dict, trigger: str = "positive_call"):
    """Send referral request to a customer"""
    
    name = customer.get('name', 'there')
    phone = customer.get('phone')
    email = customer.get('email')
    service = customer.get('service', 'our services')
    company = customer.get('company', 'AI Service Co')
    
    results = {"customer": customer, "trigger": trigger, "sent_at": datetime.now().isoformat()}
    
    # Send SMS
    if phone:
        try:
            message = REFERRAL_SMS.format(name=name.split()[0], service=service, company=company)
            requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": message})
            results["sms_sent"] = True
            print(f"[REFERRAL] SMS sent to {phone}")
        except Exception as e:
            results["sms_sent"] = False
            print(f"[ERROR] SMS failed: {e}")
    
    # Send Email
    if email and RESEND_API_KEY:
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": "AI Service Co <noreply@aiserviceco.com>",
                    "to": [email],
                    "subject": REFERRAL_EMAIL_SUBJECT,
                    "html": REFERRAL_EMAIL_BODY.format(name=name, service=service, company=company)
                }
            )
            results["email_sent"] = response.status_code == 200
            print(f"[REFERRAL] Email sent to {email}")
        except Exception as e:
            results["email_sent"] = False
            print(f"[ERROR] Email failed: {e}")
    
    return results


def process_positive_call(call_data: dict):
    """Process a positive call and trigger referral request"""
    
    # Check if call was positive (based on sentiment or booking)
    sentiment = call_data.get('sentiment', 'neutral')
    booked = call_data.get('appointment_booked', False)
    
    if sentiment == 'positive' or booked:
        customer = {
            "name": call_data.get('customer_name', 'Customer'),
            "phone": call_data.get('customer_phone'),
            "email": call_data.get('customer_email'),
            "service": call_data.get('service_type', 'HVAC service'),
            "company": "AI Service Co"
        }
        return send_referral_request(customer, "positive_call")
    
    return {"skipped": True, "reason": "Call not positive enough"}


if __name__ == "__main__":
    # Test
    test_customer = {
        "name": "John Smith",
        "phone": "+13529368152",
        "email": "test@example.com",
        "service": "AC repair",
        "company": "Cool Breeze HVAC"
    }
    
    result = send_referral_request(test_customer, "manual_test")
    print(json.dumps(result, indent=2))
