"""
HVAC CAMPAIGN LAUNCHER
======================
Finds HVAC company prospects in Florida and sends Grok-personalized outreach.
Multi-channel: Email + Sarah follow-up call.

Usage:
    python hvac_campaign.py --city "Tampa" --count 10
"""
import os
import json
import requests
import argparse
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from modules.grok_client import GrokClient

load_dotenv()

# Florida HVAC target cities
FLORIDA_CITIES = [
    "Tampa", "Orlando", "Jacksonville", "Miami", "Fort Lauderdale",
    "Lakeland", "Sarasota", "Naples", "Tallahassee", "Gainesville",
    "Pensacola", "Fort Myers", "Daytona Beach", "Clearwater", "St. Petersburg"
]

# Sample HVAC prospects (in production, these would come from scraping)
SAMPLE_PROSPECTS = {
    "Tampa": [
        {"name": "Cool Breeze HVAC", "phone": "", "email": "", "website": "coolbreezehvac.com"},
        {"name": "Florida Air Systems", "phone": "", "email": "", "website": "floridaairsystems.com"},
        {"name": "Bay Area Comfort", "phone": "", "email": "", "website": "bayareacomfort.com"},
        {"name": "Tampa Bay AC Pros", "phone": "", "email": "", "website": "tampabayacpros.com"},
    ],
    "Orlando": [
        {"name": "Magic City HVAC", "phone": "", "email": "", "website": "magiccityhvac.com"},
        {"name": "Central Florida Cooling", "phone": "", "email": "", "website": "cflcooling.com"},
        {"name": "Orlando Air Experts", "phone": "", "email": "", "website": "orlandoairexperts.com"},
    ],
    "Lakeland": [
        {"name": "Homeheart HVAC & Cool", "phone": "", "email": "", "website": "homehearthvac.com"},
        {"name": "Polk County AC", "phone": "", "email": "", "website": "polkcountyac.com"},
    ],
    "Miami": [
        {"name": "Magic City Cooling", "phone": "", "email": "", "website": "magiccitycooling.com"},
        {"name": "South Beach HVAC", "phone": "", "email": "", "website": "southbeachhvac.com"},
        {"name": "Brickell Air Systems", "phone": "", "email": "", "website": "brickellairsystems.com"},
    ],
}


def generate_prospect_email(prospect: dict, city: str) -> dict:
    """Generate a personalized email using Grok"""
    client = GrokClient()
    
    system_prompt = """You are an elite cold email copywriter for an AI phone automation company.
Write emails that:
- Open with a specific observation about their business
- Sound like a peer texting, not a salesperson
- Are under 100 words
- End with a soft question
- NO placeholder text - use actual company details"""

    prompt = f"""Write a cold email for:
Company: {prospect['name']}
City: {city}, FL
Industry: HVAC
Pain Point: After-hours emergency AC calls going to voicemail in Florida heat

Return ONLY the email body text. No subject line. Start with 'Hey' and use their company name."""

    body = client.ask(prompt, system_prompt)
    
    # Generate subject
    subject_prompt = f"Write a 5-word or less curiosity-driven subject line for a cold email to {prospect['name']} about missed after-hours calls. Just the subject, no quotes."
    subject = client.ask(subject_prompt)
    
    return {
        "subject": subject.strip().replace('"', ''),
        "body": body,
        "company": prospect['name'],
        "city": city
    }


def send_email(to_email: str, subject: str, body: str, company: str) -> bool:
    """Send email via Resend API"""
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    
    html_template = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif; background:#0f172a;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;">
<tr><td style="padding:40px 20px;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px; margin:0 auto; background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%); border-radius:16px; border:1px solid rgba(148,163,184,0.1);">
<tr><td style="padding:40px;">

<p style="color:#e2e8f0; font-size:16px; line-height:1.7; margin:0 0 20px 0;">
{body.replace(chr(10), '</p><p style="color:#e2e8f0; font-size:16px; line-height:1.7; margin:0 0 20px 0;">')}
</p>

<table cellpadding="0" cellspacing="0" style="margin:30px 0;">
<tr><td style="background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%); border-radius:10px; padding:16px 28px;">
<a href="https://calendly.com/aiserviceco/demo" style="color:#fff; text-decoration:none; font-weight:600; font-size:15px;">
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
            'subject': subject,
            'html': html_template
        }
    )
    
    return res.status_code == 200


def run_campaign(city: str = "Tampa", count: int = 5, test_email: str = None):
    """Run the HVAC campaign for a specific city"""
    print("=" * 60)
    print(f"🚀 HVAC CAMPAIGN LAUNCHER")
    print(f"Target: {city}, FL | Count: {count}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Get prospects for city
    prospects = SAMPLE_PROSPECTS.get(city, SAMPLE_PROSPECTS.get("Tampa"))[:count]
    
    campaign_log = {
        "campaign": "HVAC Florida",
        "city": city,
        "started": datetime.now().isoformat(),
        "prospects": [],
        "emails_sent": 0,
        "emails_failed": 0
    }
    
    for i, prospect in enumerate(prospects, 1):
        print(f"\n[{i}/{len(prospects)}] Processing: {prospect['name']}")
        
        # Generate email
        print(f"  🧠 Generating email with Grok...")
        email = generate_prospect_email(prospect, city)
        print(f"  📧 Subject: {email['subject']}")
        
        # For demo, send to test email
        target_email = test_email or os.getenv("TEST_EMAIL", "seaofdiscipline@gmail.com")
        
        print(f"  📤 Sending to: {target_email}")
        success = send_email(target_email, email['subject'], email['body'], prospect['name'])
        
        if success:
            print(f"  ✅ Email sent!")
            campaign_log["emails_sent"] += 1
        else:
            print(f"  ❌ Email failed")
            campaign_log["emails_failed"] += 1
        
        campaign_log["prospects"].append({
            "company": prospect['name'],
            "email_subject": email['subject'],
            "sent": success
        })
        
        # Rate limit
        if i < len(prospects):
            print(f"  ⏱️ Waiting 2s before next...")
            sleep(2)
    
    # Save campaign log
    campaign_log["completed"] = datetime.now().isoformat()
    
    log_file = f"campaign_logs/hvac_{city.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("campaign_logs", exist_ok=True)
    with open(log_file, "w") as f:
        json.dump(campaign_log, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"📊 CAMPAIGN COMPLETE")
    print(f"   Sent: {campaign_log['emails_sent']}")
    print(f"   Failed: {campaign_log['emails_failed']}")
    print(f"   Log: {log_file}")
    print("=" * 60)
    
    return campaign_log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch HVAC Campaign")
    parser.add_argument("--city", default="Tampa", help="Target city")
    parser.add_argument("--count", type=int, default=3, help="Number of prospects")
    parser.add_argument("--test-email", help="Test email to send to")
    
    args = parser.parse_args()
    
    run_campaign(args.city, args.count, args.test_email)
