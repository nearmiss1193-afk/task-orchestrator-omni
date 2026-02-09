"""
GHL Email Sender via WEBHOOK
Uses proven reliable_email.py pattern

GHL API DOES NOT WORK - Private integration only!
MUST USE WEBHOOKS - This is verified from multiple sources
"""

import requests
from datetime import datetime

# PROVEN WORKING WEBHOOK URL (from reliable_email.py)
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

# Email Template (Traffic Light Format)
EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<p>Dear {contact_name},</p>

<p>I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of {business_name}'s online presence.</p>

<p>To save you time, I have summarized the three critical areas that currently impact your online reputation, search ranking, and lead flow:</p>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
<tr style="background: #f8f9fa;">
<th style="padding: 12px; border: 1px solid #ddd; text-align: left;">AREA</th>
<th style="padding: 12px; border: 1px solid #ddd; text-align: left;">STATUS</th>
<th style="padding: 12px; border: 1px solid #ddd; text-align: left;">THE RISK TO THE BUSINESS</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #ddd;">Search Visibility</td>
<td style="padding: 12px; border: 1px solid #ddd; color: red; font-weight: bold;">CRITICAL (RED)</td>
<td style="padding: 12px; border: 1px solid #ddd;">The desktop site may be failing Google's performance standards, creating a 'hidden penalty' that makes it harder for customers to find you.</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #ddd;">Legal Compliance</td>
<td style="padding: 12px; border: 1px solid #ddd; color: orange; font-weight: bold;">WARNING (YELLOW)</td>
<td style="padding: 12px; border: 1px solid #ddd;">The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is mandatory for businesses collecting customer data.</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #ddd;">Lead Efficiency</td>
<td style="padding: 12px; border: 1px solid #ddd; color: green; font-weight: bold;">OPPORTUNITY</td>
<td style="padding: 12px; border: 1px solid #ddd;">An intelligent intake system could pre-screen calls, ensuring your team only responds to qualified service calls.</td>
</tr>
</table>

<p><strong>THE SOLUTION:</strong> I specialize in helping {industry} businesses bridge these technical gaps. I would like to offer {business_name} a 14-day "Intelligent Intake" trial. We can install a digital assistant on your site that "pre-screens" potential clients before they ever call your office.</p>

<p><strong>MY LOCAL GUARANTEE:</strong> Because I am a local Lakeland resident, I would like to fix your Search Visibility (Google Failure) for free this week. This will move your site back into the "Green" zone.</p>

<p>I will follow up with your office in an hour to see if you have any questions.</p>

<p>Best regards,</p>
<p><strong>Daniel Coffman</strong><br>
352-936-8152<br>
Owner, AI Service Co<br>
www.aiserviceco.com</p>
</body>
</html>
"""

# The 3 approved emails to send
EMAILS_TO_SEND = [
    {
        "to_email": "craig@scottsair.com",
        "contact_name": "Craig",
        "business_name": "Scott's Air Conditioning",
        "industry": "HVAC"
    },
    {
        "to_email": "allisa.sommers@airprosusa.com",
        "contact_name": "Allisa",
        "business_name": "Air Pros USA",
        "industry": "HVAC"
    },
    {
        "to_email": "tony@thelakelandac.com",
        "contact_name": "Tony",
        "business_name": "Lakeland Air Conditioning",
        "industry": "HVAC"
    }
]

def send_email_via_webhook(to_email, subject, html_body, from_name="Daniel Coffman"):
    """Send email via GHL Webhook (NOT API - API doesn't work!)"""
    payload = {
        "email": to_email,
        "from_name": from_name,
        "from_email": "owner@aiserviceco.com",
        "subject": subject,
        "html_body": html_body
    }
    
    try:
        r = requests.post(GHL_EMAIL_WEBHOOK, json=payload, timeout=30)
        if r.ok:
            print(f"✅ SENT via GHL Webhook: {to_email}")
            return {"success": True, "provider": "ghl_webhook", "response": r.text}
        else:
            print(f"❌ GHL Webhook failed: {r.status_code} - {r.text}")
            return {"success": False, "error": r.text}
    except Exception as e:
        print(f"❌ GHL Webhook exception: {e}")
        return {"success": False, "error": str(e)}

def main():
    print("=" * 60)
    print("GHL EMAIL SENDER VIA WEBHOOK")
    print("=" * 60)
    print(f"\n⚠️  GHL API does NOT work (private integration)")
    print(f"✅  Using webhook: {GHL_EMAIL_WEBHOOK[:50]}...")
    print(f"\nEmails to send: {len(EMAILS_TO_SEND)}")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for email_data in EMAILS_TO_SEND:
        print(f"\n📧 Sending to {email_data['contact_name']} at {email_data['to_email']}...")
        
        subject = f"{email_data['business_name']} - Digital Performance Audit Results"
        html_body = EMAIL_TEMPLATE.format(
            contact_name=email_data['contact_name'],
            business_name=email_data['business_name'],
            industry=email_data['industry']
        )
        
        result = send_email_via_webhook(
            to_email=email_data['to_email'],
            subject=subject,
            html_body=html_body
        )
        
        if result.get("success"):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count} sent, {fail_count} failed")
    print("=" * 60)
    
    return success_count > 0

if __name__ == "__main__":
    main()
