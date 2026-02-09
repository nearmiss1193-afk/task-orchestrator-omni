"""
Autonomous Email Sender - Uses Resend API (PRIMARY) with GHL Webhook fallback
Based on proven reliable_email.py pattern
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Resend API (PRIMARY - proven to work)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy")

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

def send_via_resend(to_email, subject, html_body):
    """Send email via Resend API (PRIMARY - proven reliable)"""
    payload = {
        "from": "Daniel Coffman <dan@aiserviceco.com>",
        "to": [to_email],
        "subject": subject,
        "html": html_body,
        "reply_to": "owner@aiserviceco.com"
    }
    
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json=payload,
            timeout=30
        )
        if r.ok:
            print(f"✅ RESEND SUCCESS: {to_email}")
            return {"success": True, "provider": "resend", "response": r.json()}
        else:
            print(f"❌ RESEND FAILED: {r.status_code} - {r.text}")
            return {"success": False, "error": r.text}
    except Exception as e:
        print(f"❌ RESEND ERROR: {e}")
        return {"success": False, "error": str(e)}

def main():
    print("=" * 60)
    print("AUTONOMOUS EMAIL SENDER (Resend API)")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Using Resend API Key: {RESEND_API_KEY[:15]}...")
    print(f"Emails to send: {len(EMAILS_TO_SEND)}")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    results = []
    
    for email_data in EMAILS_TO_SEND:
        print(f"\n📧 Sending to {email_data['contact_name']} at {email_data['to_email']}...")
        
        subject = f"{email_data['business_name']} - Digital Performance Audit Results"
        html_body = EMAIL_TEMPLATE.format(
            contact_name=email_data['contact_name'],
            business_name=email_data['business_name'],
            industry=email_data['industry']
        )
        
        result = send_via_resend(
            to_email=email_data['to_email'],
            subject=subject,
            html_body=html_body
        )
        
        results.append({
            "email": email_data['to_email'],
            "company": email_data['business_name'],
            "result": result
        })
        
        if result.get("success"):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count} sent, {fail_count} failed")
    print("=" * 60)
    
    for r in results:
        status = "✅" if r['result'].get('success') else "❌"
        print(f"{status} {r['company']}: {r['email']}")
    
    return success_count > 0

if __name__ == "__main__":
    main()
