"""
GHL Email Workflow Setup Script
Creates a NEW webhook for outbound emails (doesn't modify existing)

MANUAL STEPS IN GHL:
1. Go to GHL Dashboard: https://app.gohighlevel.com
2. Navigate to: Automation -> Workflows
3. Click "+ Create Workflow"
4. Name it: "Outbound Email - Sarah Audit"
5. Choose trigger: "Webhook"
6. Add action: "Send Email"
   - From Name: Sarah
   - From Email: sarah@aiserviceco.com (or your verified sender)
   - To: {{contact.email}}
   - Subject: Use custom field {{custom.subject}}
   - Body: Use custom field {{custom.body}}
7. Publish the workflow
8. Copy the webhook URL
9. Update the webhook URL below

After setting up, test with:
    python ghl_email_workflow.py test
"""
import requests
import os

# REPLACE THIS with your new GHL outbound email webhook URL
# Get this from GHL when you create the new workflow
GHL_OUTBOUND_EMAIL_WEBHOOK = os.getenv(
    "GHL_OUTBOUND_EMAIL_WEBHOOK",
    "https://services.leadconnectorhq.com/hooks/YOUR_NEW_WEBHOOK_HERE"
)

def send_outbound_email(to_email, subject, body, contact_name=""):
    """Send email through GHL workflow"""
    
    # Check if webhook is configured
    if "YOUR_NEW_WEBHOOK_HERE" in GHL_OUTBOUND_EMAIL_WEBHOOK:
        print("[WARNING] GHL_OUTBOUND_EMAIL_WEBHOOK not configured!")
        print("Please follow the setup instructions at the top of this file.")
        return False
    
    payload = {
        "email": to_email,
        "contact_name": contact_name,
        "subject": subject,
        "body": body
    }
    
    try:
        resp = requests.post(
            GHL_OUTBOUND_EMAIL_WEBHOOK,
            json=payload,
            timeout=15
        )
        
        if resp.status_code == 200:
            print(f"[GHL EMAIL] Sent to {to_email}")
            return True
        else:
            print(f"[GHL EMAIL ERROR] {resp.status_code}: {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"[GHL EMAIL ERROR] {e}")
        return False

def test_workflow():
    """Test the GHL email workflow"""
    print("=" * 50)
    print("TESTING GHL OUTBOUND EMAIL WORKFLOW")
    print("=" * 50)
    
    result = send_outbound_email(
        to_email="nearmiss1193@gmail.com",
        subject="Test - GHL Outbound Email Workflow",
        body="This is a test email sent through the new GHL outbound workflow.",
        contact_name="Test User"
    )
    
    if result:
        print("\n[SUCCESS] Email sent! Check your inbox.")
    else:
        print("\n[FOLLOW SETUP INSTRUCTIONS ABOVE]")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_workflow()
    else:
        print(__doc__)
