"""
SMS Sender via Twilio
======================
Bypasses GHL SMS scope issue by using Twilio directly.
"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')

def send_sms(to_number: str, message: str) -> dict:
    """Send SMS via Twilio"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    msg = client.messages.create(
        body=message,
        from_=TWILIO_FROM_NUMBER,
        to=to_number
    )
    
    return {
        "sid": msg.sid,
        "status": msg.status,
        "to": to_number
    }

if __name__ == "__main__":
    # Test SMS
    TEST_PHONE = os.getenv('TEST_PHONE')
    result = send_sms(
        TEST_PHONE,
        "Hey! This is Sarah from AI Service Co. Just sent you an email about saving revenue on missed calls. Worth a quick look? - Sarah"
    )
    print(f"SMS sent! SID: {result['sid']}, Status: {result['status']}")
