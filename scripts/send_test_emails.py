"""
Send test emails via GHL Email Webhook - CORRECT URL from GHL dashboard
Workflow: "outbound emails prospects21ST"
"""
import requests
from datetime import datetime

# CORRECT GHL Email Webhook from user's GHL workflow screenshot
# Workflow: "outbound emails prospects21ST"
GHL_OUTBOUND_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

# Email to send
DAN_EMAIL = "nearmiss1193@gmail.com"

# Test Email Content
EMAIL_SUBJECT = "[TEST] Scott's Air Conditioning - Digital Performance Audit"
EMAIL_BODY = """Dear Craig,

I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of Scott's Air Conditioning's online presence.

To save you time, I have summarized the three critical areas that currently impact your online reputation, search ranking, and lead flow:

AREA                 STATUS              THE RISK TO THE BUSINESS
---------------------------------------------------------------------------
Search Visibility    CRITICAL            The desktop site may be failing Google's performance standards, creating a 'hidden penalty' that makes it harder for customers to find you when their AC breaks down.

Legal Compliance     WARNING             The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is mandatory for businesses collecting customer data via web forms.

Lead Efficiency      OPPORTUNITY         Currently, your staff may be manually fielding every inquiry. An intelligent intake system could pre-screen calls, ensuring your technicians only respond to qualified service calls.

THE SOLUTION: I specialize in helping HVAC businesses bridge these technical gaps. I would like to offer Scott's Air Conditioning a 14-day "Intelligent Intake" trial.

MY LOCAL GUARANTEE: Because I am a local Lakeland resident, I would like to fix your Search Visibility (Google Failure) for free this week.

Best regards,

Daniel Coffman
352-936-8152
Owner, AI Service Co
www.aiserviceco.com
"""

print("=" * 60)
print(f"SENDING TEST EMAIL VIA CORRECT GHL WEBHOOK")
print(f"Time: {datetime.now().strftime('%I:%M %p')}")
print(f"Webhook: ...uKaqY2KaULkCeMHM7wmt")
print(f"To: {DAN_EMAIL}")
print("=" * 60)

# Based on the workflow flow (Create Contact → Wait → Drip Mode → Send mapped email)
# The webhook likely expects contact fields that get mapped
payload = {
    # Standard contact fields for GHL
    "email": DAN_EMAIL,
    "firstName": "Test",
    "lastName": "User",
    "phone": "+13529368152",
    # Email-specific fields for "Send mapped email" action
    "subject": EMAIL_SUBJECT,
    "message": EMAIL_BODY,
    "body": EMAIL_BODY,
    # Optional custom fields
    "customField": {
        "emailSubject": EMAIL_SUBJECT,
        "emailBody": EMAIL_BODY
    }
}

print("\n[SENDING]...")
try:
    r = requests.post(GHL_OUTBOUND_EMAIL_WEBHOOK, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    
    if r.status_code == 200:
        print("\n✅ Webhook accepted request!")
        print("Check GHL Execution Logs to verify if email was sent.")
    else:
        print(f"\n⚠️ Non-200 status: {r.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

print(f"\n📧 Check inbox at {DAN_EMAIL}")
