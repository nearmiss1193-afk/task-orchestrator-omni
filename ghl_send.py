"""
GHL UNIFIED SEND - Email and SMS through GHL webhooks
"""
import requests

# =============================================================================
# GHL WEBHOOKS - Verified working webhooks
# =============================================================================

# SMS Webhook - Triggers workflow that sends SMS
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Email Webhook - Triggers workflow that sends email
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/cf2e8a9c-e943-4d78-9f6f-cd66bb9a2e42"


def send_sms(phone: str, message: str) -> dict:
    """
    Send SMS via GHL workflow webhook
    The GHL workflow must be configured to:
    1. Receive webhook with phone and message
    2. Send SMS to the phone number with the message
    """
    try:
        r = requests.post(
            GHL_SMS_WEBHOOK,
            json={"phone": phone, "message": message},
            timeout=15
        )
        return {"success": r.status_code in [200, 201], "status": r.status_code, "response": r.text[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_email(to_email: str, subject: str, body: str, from_name: str = "Sarah", company: str = "") -> dict:
    """
    Send Email via GHL workflow webhook
    The GHL workflow must be configured to:
    1. Receive webhook with email, subject, body
    2. Send email to the recipient
    """
    try:
        r = requests.post(
            GHL_EMAIL_WEBHOOK,
            json={
                "email": to_email,
                "subject": subject,
                "body": body,
                "from_name": from_name,
                "company": company
            },
            timeout=15
        )
        return {"success": r.status_code in [200, 201], "status": r.status_code, "response": r.text[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_sms():
    """Test SMS sending"""
    print("=" * 60)
    print("TESTING GHL SMS")
    print("=" * 60)
    
    result = send_sms(
        phone="+13529368152",  # Owner phone
        message="🧪 Test SMS from Empire Unified - GHL integration working!"
    )
    print(f"Result: {result}")
    return result


def test_email():
    """Test email sending"""
    print("\n" + "=" * 60)
    print("TESTING GHL EMAIL")
    print("=" * 60)
    
    result = send_email(
        to_email="nearmiss1193@gmail.com",
        subject="🧪 Test Email - GHL Integration",
        body="This is a test email sent via GHL workflow webhook.",
        from_name="Sarah",
        company="AI Service Co"
    )
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    print("\n🔄 Testing GHL Email & SMS Integration\n")
    
    sms_result = test_sms()
    email_result = test_email()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"SMS: {'✅ WORKING' if sms_result.get('success') else '❌ FAILED'}")
    print(f"Email: {'✅ WORKING' if email_result.get('success') else '❌ FAILED'}")
