"""
HVAC EMAIL CAMPAIGN WITH VIDEO - FULL BLAST
============================================
Sends Grok-personalized emails with video link to all 20 top prospects.

Usage:
    python blast_hvac_campaign.py
"""
import os
import json
import resend
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from modules.grok_client import GrokClient

# Configuration
resend.api_key = os.getenv('RESEND_API_KEY')
VIDEO_URL = "https://youtube.com/shorts/C4GRQ8xaFn0"
VIDEO_THUMBNAIL = "https://i.ytimg.com/vi/C4GRQ8xaFn0/maxresdefault.jpg"
CALENDLY_LINK = "https://calendly.com/aiserviceco/demo"

# Load both batches of prospects
CAMPAIGN_DATA_DIR = "campaign_data"


def load_all_prospects():
    """Load all prospects from both batch files"""
    all_prospects = []
    
    for filename in os.listdir(CAMPAIGN_DATA_DIR):
        if filename.startswith("top10") and filename.endswith(".json"):
            filepath = os.path.join(CAMPAIGN_DATA_DIR, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                prospects = data.get("top_10_prospects", [])
                all_prospects.extend(prospects)
    
    return all_prospects


def create_video_email_html(prospect, personalized_message):
    """Create premium HTML email with embedded video thumbnail"""
    company = prospect.get("company_name", "Your Company")
    contact = prospect.get("contacts", [{}])[0]
    contact_name = contact.get("name", "there").split()[0]  # First name only
    savings = prospect.get("savings_analysis", {})
    monthly_loss = savings.get("monthly_lost_revenue", 10000)
    annual_savings = savings.get("net_annual_savings", 100000)
    roi = savings.get("roi_multiplier", 50)
    
    subject = personalized_message.get("subject", f"Quick question for {company}")
    body = personalized_message.get("body", "")
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#0f172a;font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
        
        <!-- Header -->
        <div style="text-align:center;margin-bottom:30px;">
            <h1 style="color:#f8fafc;font-size:24px;margin:0;">AI Service Co</h1>
            <p style="color:#64748b;font-size:14px;margin:5px 0;">24/7 AI Phone Agents for Service Businesses</p>
        </div>
        
        <!-- Personal Greeting -->
        <div style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);border:1px solid #334155;border-radius:16px;padding:30px;margin-bottom:30px;">
            <p style="color:#f8fafc;font-size:18px;line-height:1.6;margin:0 0 20px 0;">
                Hey {contact_name},
            </p>
            <p style="color:#94a3b8;font-size:16px;line-height:1.7;margin:0;">
                {body.replace(chr(10), '<br>')}
            </p>
        </div>
        
        <!-- Video Section -->
        <div style="background:#1e293b;border:1px solid #334155;border-radius:16px;overflow:hidden;margin-bottom:30px;">
            <a href="{VIDEO_URL}" target="_blank" style="display:block;position:relative;">
                <img src="{VIDEO_THUMBNAIL}" alt="Watch Video" style="width:100%;height:auto;display:block;">
                <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80px;height:80px;background:rgba(37,99,235,0.9);border-radius:50%;display:flex;align-items:center;justify-content:center;">
                    <div style="width:0;height:0;border-left:30px solid white;border-top:18px solid transparent;border-bottom:18px solid transparent;margin-left:8px;"></div>
                </div>
            </a>
            <div style="padding:20px;text-align:center;">
                <p style="color:#60a5fa;font-size:14px;margin:0;font-weight:600;">
                    ▶️ Watch: How We Save HVAC Companies ${monthly_loss:,.0f}/Month
                </p>
            </div>
        </div>
        
        <!-- Stats Box -->
        <div style="background:linear-gradient(135deg,#14532d 0%,#166534 100%);border-radius:16px;padding:25px;margin-bottom:30px;">
            <h3 style="color:#f8fafc;font-size:16px;margin:0 0 15px 0;text-align:center;">
                📊 Your Estimated Numbers
            </h3>
            <div style="display:flex;justify-content:space-around;text-align:center;">
                <div>
                    <p style="color:#4ade80;font-size:28px;font-weight:700;margin:0;">${monthly_loss:,.0f}</p>
                    <p style="color:#86efac;font-size:12px;margin:5px 0 0 0;">Monthly Lost Revenue</p>
                </div>
                <div>
                    <p style="color:#4ade80;font-size:28px;font-weight:700;margin:0;">${annual_savings:,.0f}</p>
                    <p style="color:#86efac;font-size:12px;margin:5px 0 0 0;">Annual Savings</p>
                </div>
                <div>
                    <p style="color:#4ade80;font-size:28px;font-weight:700;margin:0;">{roi}x</p>
                    <p style="color:#86efac;font-size:12px;margin:5px 0 0 0;">ROI</p>
                </div>
            </div>
        </div>
        
        <!-- CTA Button -->
        <div style="text-align:center;margin-bottom:30px;">
            <a href="{CALENDLY_LINK}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);color:white;text-decoration:none;padding:18px 40px;border-radius:12px;font-size:16px;font-weight:600;">
                📅 Book Your Free Demo (10 min)
            </a>
        </div>
        
        <!-- Signature -->
        <div style="border-top:1px solid #334155;padding-top:20px;text-align:center;">
            <p style="color:#94a3b8;font-size:14px;margin:0 0 5px 0;">
                Daniel | AI Service Co
            </p>
            <p style="color:#64748b;font-size:12px;margin:0;">
                Reply to this email or call (352) 936-8152
            </p>
            <p style="color:#475569;font-size:11px;margin:15px 0 0 0;">
                AI-powered phone agents for HVAC, plumbing, and home services.
            </p>
        </div>
        
    </div>
</body>
</html>
"""
    return subject, html


def send_campaign():
    """Send video email campaign to all prospects"""
    print("=" * 70)
    print("🚀 HVAC VIDEO EMAIL CAMPAIGN - FULL BLAST")
    print(f"Video: {VIDEO_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Load prospects
    prospects = load_all_prospects()
    print(f"\n📊 Loaded {len(prospects)} prospects from campaign data")
    
    results = {
        "sent": [],
        "failed": [],
        "timestamp": datetime.now().isoformat(),
        "video_url": VIDEO_URL
    }
    
    for i, prospect in enumerate(prospects, 1):
        company = prospect.get("company_name", "Unknown")
        contacts = prospect.get("contacts", [])
        
        if not contacts:
            print(f"[{i}/{len(prospects)}] ⚠️ {company} - No contacts, skipping")
            continue
        
        contact = contacts[0]
        email = contact.get("email")
        name = contact.get("name", "Unknown")
        
        if not email:
            print(f"[{i}/{len(prospects)}] ⚠️ {company} - No email, skipping")
            continue
        
        # Get personalized message from prospect data
        personalized_message = prospect.get("personalized_message", {
            "subject": f"Quick question about {company}",
            "body": "I noticed you might be missing calls after hours..."
        })
        
        # Create HTML email
        subject, html = create_video_email_html(prospect, personalized_message)
        
        print(f"[{i}/{len(prospects)}] 📧 Sending to {name} at {company}...")
        
        try:
            params = {
                "from": "Daniel <daniel@aiserviceco.com>",
                "to": [email],
                "reply_to": "owner@aiserviceco.com",
                "subject": subject,
                "html": html
            }
            
            response = resend.Emails.send(params)
            
            results["sent"].append({
                "company": company,
                "contact": name,
                "email": email,
                "subject": subject,
                "response_id": response.get("id") if isinstance(response, dict) else str(response)
            })
            
            print(f"    ✅ Sent!")
            
        except Exception as e:
            results["failed"].append({
                "company": company,
                "contact": name,
                "email": email,
                "error": str(e)
            })
            print(f"    ❌ Failed: {e}")
    
    # Save results
    os.makedirs("campaign_logs", exist_ok=True)
    log_file = f"campaign_logs/video_blast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"📊 CAMPAIGN COMPLETE")
    print(f"   ✅ Sent: {len(results['sent'])}")
    print(f"   ❌ Failed: {len(results['failed'])}")
    print(f"   📁 Log: {log_file}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    send_campaign()
