"""
SCHEDULED CAMPAIGN RUNNER
=========================
Schedule emails at 7am, SMS at 10am for prospect campaigns.
"""
import os
import json
import time
import schedule
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Campaign prospects - loaded from file or defined here
CAMPAIGN_PROSPECTS = []


def load_prospects(filename: str = "campaign_prospects.json") -> list:
    """Load prospects from JSON file"""
    global CAMPAIGN_PROSPECTS
    
    try:
        with open(filename, "r") as f:
            CAMPAIGN_PROSPECTS = json.load(f)
            print(f"[CAMPAIGN] Loaded {len(CAMPAIGN_PROSPECTS)} prospects")
            return CAMPAIGN_PROSPECTS
    except FileNotFoundError:
        print(f"[CAMPAIGN] No {filename} found - create one or add prospects manually")
        return []


def send_campaign_email(prospect: dict) -> bool:
    """Send campaign email to a prospect"""
    
    if not RESEND_API_KEY:
        print(f"[EMAIL] Mock send to {prospect.get('email')}")
        return True
    
    email_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>Hey {prospect.get('name', 'there').split()[0]},</h2>
    
    <p>I noticed {prospect.get('company', 'your business')} might be missing calls after hours. Quick question:</p>
    
    <p><strong>How many calls do you think you miss each week when you're busy on the job?</strong></p>
    
    <p>We've helped businesses like yours capture 30% more leads with our 24/7 AI receptionist. It answers calls, books appointments, and never takes a day off.</p>
    
    <p><a href="https://aiserviceco.com?utm_source=email&utm_campaign=jan08" style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none;">See How It Works →</a></p>
    
    <p>Reply to this email if you have any questions!</p>
    
    <p>Best,<br>
    Sarah<br>
    AI Service Co<br>
    (863) 213-2505</p>
    </body>
    </html>
    """
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": "Sarah <sarah@aiserviceco.com>",
                "to": [prospect.get('email')],
                "cc": ["owner@aiserviceco.com"],  # Send copy to owner
                "subject": f"Quick question about {prospect.get('company', 'your business')}'s missed calls",
                "html": email_html
            }
        )
        
        if response.status_code == 200:
            print(f"[EMAIL] ✅ Sent to {prospect.get('email')}")
            return True
        else:
            print(f"[EMAIL] ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"[EMAIL] ❌ Error: {e}")
        return False


def send_campaign_sms(prospect: dict) -> bool:
    """Send campaign SMS to a prospect"""
    
    phone = prospect.get('phone')
    if not phone:
        return False
    
    message = f"Hey {prospect.get('name', 'there').split()[0]}! Sarah from AI Service Co here. Saw your business might be losing calls after hours. Mind if I show you a 30-second fix? No pressure - just reply YES if curious."
    
    try:
        response = requests.post(GHL_SMS_WEBHOOK, json={
            "phone": phone,
            "message": message
        })
        
        print(f"[SMS] ✅ Sent to {phone}")
        return True
    except Exception as e:
        print(f"[SMS] ❌ Error: {e}")
        return False


def run_7am_emails():
    """Run email campaign at 7am"""
    print(f"\n{'='*50}")
    print(f"[CAMPAIGN] 7AM EMAIL BLAST - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")
    
    if not CAMPAIGN_PROSPECTS:
        load_prospects()
    
    sent = 0
    for prospect in CAMPAIGN_PROSPECTS:
        if prospect.get('email'):
            if send_campaign_email(prospect):
                sent += 1
            time.sleep(1)  # Rate limit
    
    print(f"[CAMPAIGN] Emails sent: {sent}/{len(CAMPAIGN_PROSPECTS)}")
    
    # Log results
    log_campaign_results("email", sent)


def run_10am_sms():
    """Run SMS campaign at 10am"""
    print(f"\n{'='*50}")
    print(f"[CAMPAIGN] 10AM SMS BLAST - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")
    
    if not CAMPAIGN_PROSPECTS:
        load_prospects()
    
    sent = 0
    for prospect in CAMPAIGN_PROSPECTS:
        if prospect.get('phone'):
            if send_campaign_sms(prospect):
                sent += 1
            time.sleep(2)  # Rate limit for SMS
    
    print(f"[CAMPAIGN] SMS sent: {sent}/{len(CAMPAIGN_PROSPECTS)}")
    
    # Log results
    log_campaign_results("sms", sent)


def log_campaign_results(campaign_type: str, sent: int):
    """Log campaign results"""
    log_file = "campaign_logs/scheduled_campaigns.json"
    os.makedirs("campaign_logs", exist_ok=True)
    
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append({
        "type": campaign_type,
        "sent": sent,
        "total_prospects": len(CAMPAIGN_PROSPECTS),
        "timestamp": datetime.now().isoformat()
    })
    
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


def schedule_campaign():
    """Schedule the campaign"""
    
    # Schedule 7am emails (Eastern Time)
    schedule.every().day.at("07:00").do(run_7am_emails)
    
    # Schedule 10am SMS (Eastern Time)
    schedule.every().day.at("10:00").do(run_10am_sms)
    
    print(f"[SCHEDULER] Campaign scheduled:")
    print(f"  📧 Emails at 7:00 AM")
    print(f"  💬 SMS at 10:00 AM")
    print(f"  📊 Prospects loaded: {len(CAMPAIGN_PROSPECTS)}")
    print(f"\n[SCHEDULER] Running... (Ctrl+C to stop)")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def preview_campaign():
    """Preview what will be sent"""
    load_prospects()
    
    print(f"\n📧 EMAIL PREVIEW ({len([p for p in CAMPAIGN_PROSPECTS if p.get('email')])} recipients):")
    for p in CAMPAIGN_PROSPECTS[:5]:
        if p.get('email'):
            print(f"  - {p.get('name')}: {p.get('email')}")
    
    print(f"\n💬 SMS PREVIEW ({len([p for p in CAMPAIGN_PROSPECTS if p.get('phone')])} recipients):")
    for p in CAMPAIGN_PROSPECTS[:5]:
        if p.get('phone'):
            print(f"  - {p.get('name')}: {p.get('phone')}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "preview":
            preview_campaign()
        elif cmd == "email-now":
            load_prospects()
            run_7am_emails()
        elif cmd == "sms-now":
            load_prospects()
            run_10am_sms()
        elif cmd == "run":
            load_prospects()
            schedule_campaign()
        else:
            print("Usage: python scheduled_campaign.py [preview|email-now|sms-now|run]")
    else:
        # Default: load and preview
        load_prospects()
        preview_campaign()
        print("\nTo start scheduled campaign: python scheduled_campaign.py run")
