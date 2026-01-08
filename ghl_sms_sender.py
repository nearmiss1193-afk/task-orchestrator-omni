"""
GHL SMS SENDER - Using Webhook (No API Token Required)
Learned: Jan 7, 2026
"""

import requests

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

def send_sms(phone: str, message: str) -> dict:
    """
    Send SMS via GHL webhook.
    
    Args:
        phone: Phone number with country code (e.g., +13529368152)
        message: SMS message content
    
    Returns:
        dict with status and response
    """
    response = requests.post(
        GHL_SMS_WEBHOOK,
        json={"phone": phone, "message": message},
        headers={"Content-Type": "application/json"}
    )
    return {
        "status": response.status_code,
        "success": response.status_code == 200,
        "response": response.text[:200]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        phone = sys.argv[1]
        message = " ".join(sys.argv[2:])
        result = send_sms(phone, message)
        print(f"SMS {'sent' if result['success'] else 'failed'}: {result}")
    else:
        print("Usage: python ghl_sms_sender.py +1XXXXXXXXXX 'Your message'")
