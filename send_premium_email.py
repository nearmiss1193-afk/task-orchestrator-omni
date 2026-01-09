"""
PREMIUM PROSPECT EMAIL SENDER
============================
Sends beautifully styled HTML email using Grok for personalization.
"""
import os
import requests
from dotenv import load_dotenv
from modules.grok_client import GrokClient

load_dotenv()

def send_premium_email(
    to_email: str,
    company: str,
    industry: str = "HVAC",
    location: str = "Florida"
):
    """Generate and send a premium styled cold email"""
    
    # Generate personalized content with Grok
    client = GrokClient()
    
    prompt = f"""Write a 3-sentence cold email opening for:
Company: {company}
Industry: {industry}
Location: {location}
Pain: After-hours calls going unanswered, losing emergency jobs

Make it sound like a peer texting, not a salesperson. No placeholder text. Start with 'Hey' and their company name."""

    email_body = client.ask(prompt)
    
    # Premium HTML template
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif; background:#0f172a;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;">
<tr><td style="padding:40px 20px;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px; margin:0 auto; background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%); border-radius:16px; border:1px solid rgba(148,163,184,0.1);">
<tr><td style="padding:40px;">

<p style="color:#e2e8f0; font-size:16px; line-height:1.7; margin:0 0 20px 0;">
{email_body}
</p>

<p style="color:#e2e8f0; font-size:16px; line-height:1.7; margin:0 0 20px 0;">
I put together a quick 60-second video showing how one HVAC company turned missed calls into $12K/month. Worth a look?
</p>

<table cellpadding="0" cellspacing="0" style="margin:30px 0;">
<tr><td style="background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%); border-radius:10px; padding:16px 28px;">
<a href="https://www.aiserviceco.com/features.html" style="color:#fff; text-decoration:none; font-weight:600; font-size:15px;">
📞 Book a Quick Chat
</a>
</td></tr>
</table>

<table cellpadding="0" cellspacing="0" style="margin-top:30px; border-top:1px solid rgba(148,163,184,0.1); padding-top:20px;">
<tr><td style="color:#94a3b8; font-size:14px;">
<p style="margin:0 0 5px 0; color:#e2e8f0; font-weight:600;">Daniel</p>
<p style="margin:0; color:#64748b;">AI Service Co · <a href="https://aiserviceco.com" style="color:#3b82f6;">aiserviceco.com</a></p>
</td></tr>
</table>

</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

    # Send via Resend
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    
    res = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'Daniel @ AI Service Co <system@aiserviceco.com>',
            'reply_to': 'owner@aiserviceco.com',
            'to': to_email,
            'subject': f'Quick question for {company}',
            'html': html
        }
    )
    
    if res.status_code == 200:
        print(f"✅ Premium email sent to {to_email}")
        print(f"Generated content: {email_body[:100]}...")
        return True
    else:
        print(f"❌ Failed: {res.status_code} - {res.text}")
        return False


if __name__ == "__main__":
    send_premium_email(
        to_email="seaofdiscipline@gmail.com",
        company="Homeheart HVAC & Cool",
        industry="HVAC",
        location="Lakeland, FL"
    )
