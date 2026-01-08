"""
GHL Webhook Bridge
==================
The "Ping-Pong" communication system for GHL $99 plan.
Bypasses API limitations by using GHL Workflows + Incoming Webhooks.

ARCHITECTURE:
- Agent → GHL: Hit GHL Incoming Webhook URL → GHL Workflow sends SMS/Email
- GHL → Agent: GHL Workflow triggers → Sends webhook to our endpoint

SETUP REQUIRED IN GHL:
1. Go to Automation > Workflows > Create New
2. Trigger: "Incoming Webhook" (copy the generated URL)
3. Action: "Send SMS" with {{webhook.message}} as body
4. Enable "Allow Multiple"
5. Publish

USAGE:
    from ghl_webhook_bridge import send_sms, send_email
    send_sms("+15550000000", "Hello from Sarah!")
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# GHL Webhook URLs - Set these from GHL Workflow setup
GHL_SMS_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL', '')
GHL_EMAIL_WEBHOOK_URL = os.getenv('GHL_EMAIL_WEBHOOK_URL', '')
GHL_CALL_WEBHOOK_URL = os.getenv('GHL_CALL_WEBHOOK_URL', '')

# Vapi config for call triggers
VAPI_PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID')
VAPI_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah 3.1


def send_sms(phone: str, message: str, name: str = None) -> dict:
    """
    Send SMS via GHL Webhook Bridge.
    GHL Workflow handles the actual sending using your SMS credits.
    """
    if not GHL_SMS_WEBHOOK_URL:
        return {
            "success": False,
            "error": "GHL_SMS_WEBHOOK_URL not configured. Set up GHL workflow first.",
            "setup_instructions": """
1. Go to GHL > Automation > Workflows > Create New
2. Trigger: 'Incoming Webhook' (copy URL)
3. Action: 'Send SMS' with {{webhook.message}}
4. Add GHL_SMS_WEBHOOK_URL=<your_url> to .env
            """
        }
    
    payload = {
        "phone": phone,
        "message": message,
        "name": name or "Prospect",
        "source": "antigravity_agent",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(GHL_SMS_WEBHOOK_URL, json=payload, timeout=10)
        return {
            "success": response.status_code in [200, 201, 202],
            "provider": "ghl_webhook",
            "status_code": response.status_code,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_email(email: str, subject: str, body: str, name: str = None) -> dict:
    """
    Send email via GHL Webhook Bridge.
    """
    if not GHL_EMAIL_WEBHOOK_URL:
        # Fallback to Resend
        import resend
        resend.api_key = os.getenv('RESEND_API_KEY')
        
        try:
            result = resend.Emails.send({
                "from": "Daniel <daniel@aiserviceco.com>",
                "to": [email],
                "reply_to": "owner@aiserviceco.com",
                "subject": subject,
                "html": body
            })
            return {
                "success": True,
                "provider": "resend_fallback",
                "message_id": result.get("id")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    payload = {
        "email": email,
        "subject": subject,
        "body": body,
        "name": name or "Prospect",
        "source": "antigravity_agent",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(GHL_EMAIL_WEBHOOK_URL, json=payload, timeout=10)
        return {
            "success": response.status_code in [200, 201, 202],
            "provider": "ghl_webhook",
            "status_code": response.status_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def trigger_sarah_call(phone: str, name: str = None) -> dict:
    """
    Trigger a Sarah call via GHL Webhook.
    GHL Workflow will call Vapi API to initiate the call.
    
    OR call Vapi directly (this still works via API).
    """
    # Direct Vapi call (API still works)
    vapi_url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {os.getenv('VAPI_PRIVATE_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "assistantId": VAPI_ASSISTANT_ID,
        "customer": {
            "number": phone,
            "name": name or "Prospect"
        }
    }
    
    try:
        response = requests.post(vapi_url, headers=headers, json=payload, timeout=30)
        return {
            "success": response.status_code in [200, 201],
            "provider": "vapi_direct",
            "status_code": response.status_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# GHL Workflow templates for quick reference
GHL_WORKFLOW_TEMPLATES = """
=== GHL WORKFLOW SETUP GUIDE ===

1. SMS WORKFLOW (Agent → GHL → Customer)
   - Trigger: Incoming Webhook
   - Action: Send SMS
   - Message: {{webhook.message}}
   - To: {{webhook.phone}}
   - Enable: Allow Multiple

2. EMAIL WORKFLOW (Agent → GHL → Customer)  
   - Trigger: Incoming Webhook
   - Action: Send Email
   - Subject: {{webhook.subject}}
   - Body: {{webhook.body}}
   - To: {{webhook.email}}

3. CALL WORKFLOW (GHL → Sarah)
   - Trigger: Tag Added "call-sarah"
   - Action: External Webhook (POST)
   - URL: https://api.vapi.ai/call/phone
   - Headers: Authorization: Bearer YOUR_VAPI_KEY
   - Body: {"phoneNumberId":"...", "assistantId":"...", "customer":{"number":"{{contact.phone}}"}}

4. INBOUND SMS HANDLER (Customer → GHL → Agent)
   - Trigger: Customer Replied (SMS)
   - Action: External Webhook
   - URL: YOUR_AGENT_ENDPOINT (Supabase Edge Function or Modal webhook)
   - Body: Full contact + message payload
"""


if __name__ == "__main__":
    print("=== GHL Webhook Bridge ===")
    print("\nChecking configuration...")
    print(f"SMS Webhook URL: {'✅ Set' if GHL_SMS_WEBHOOK_URL else '❌ Not set'}")
    print(f"Email Webhook URL: {'✅ Set' if GHL_EMAIL_WEBHOOK_URL else '❌ Not set (using Resend fallback)'}")
    print(f"Vapi Phone ID: {'✅ Set' if VAPI_PHONE_NUMBER_ID else '❌ Not set'}")
    
    print("\n" + GHL_WORKFLOW_TEMPLATES)
    
    # Test if webhook URLs are set
    if not GHL_SMS_WEBHOOK_URL:
        print("\n⚠️  To enable GHL SMS, add to your .env file:")
        print("    GHL_SMS_WEBHOOK_URL=https://services.leadconnectorhq.com/hooks/YOUR_ID")
