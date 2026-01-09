"""
SMS FOLLOW-UP BLAST - SCHEDULED FOR 4 PM
=========================================
Sends SMS with video link to all prospects.
Uses Twilio as fallback since GHL has scope issues.

Usage:
    python sms_blast_4pm.py          # Run immediately
    python sms_blast_4pm.py --wait   # Wait until 4 PM then send
"""
import os
import json
import time
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Try Twilio first (more reliable)
try:
    from twilio.rest import Client as TwilioClient
    HAS_TWILIO = True
except ImportError:
    HAS_TWILIO = False
    print("⚠️ Twilio not installed. Run: pip install twilio")

# Configuration
VIDEO_URL = "https://youtube.com/shorts/C4GRQ8xaFn0"
CALENDLY_LINK = "https://www.aiserviceco.com/features.html"
CAMPAIGN_DATA_DIR = "campaign_data"

# Twilio credentials (set these in .env)
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER", "+13529368152")


def load_all_prospects():
    """Load all prospects from campaign data"""
    all_prospects = []
    
    for filename in os.listdir(CAMPAIGN_DATA_DIR):
        if filename.startswith("top10") and filename.endswith(".json"):
            filepath = os.path.join(CAMPAIGN_DATA_DIR, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                prospects = data.get("top_10_prospects", [])
                all_prospects.extend(prospects)
    
    return all_prospects


def create_sms_message(prospect):
    """Create personalized SMS message"""
    company = prospect.get("company_name", "your company")
    contact = prospect.get("contacts", [{}])[0]
    name = contact.get("name", "").split()[0] if contact.get("name") else ""
    savings = prospect.get("savings_analysis", {})
    monthly_loss = savings.get("monthly_lost_revenue", 10000)
    
    # Keep SMS short and punchy
    message = f"""Hey{' ' + name if name else ''}! This is Daniel from AI Service Co.

Saw you might be losing ${int(monthly_loss):,}/mo to missed after-hours calls at {company}.

Quick 45-sec video on how we fix that: {VIDEO_URL}

Reply YES for a quick demo or book here: {CALENDLY_LINK}"""
    
    return message


def wait_until_4pm():
    """Wait until 4 PM EST"""
    now = datetime.now()
    target = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if now >= target:
        print("⚠️ It's already past 4 PM. Sending immediately.")
        return
    
    wait_seconds = (target - now).total_seconds()
    print(f"⏰ Waiting until 4:00 PM EST ({wait_seconds/60:.1f} minutes)...")
    print(f"   Current time: {now.strftime('%I:%M %p')}")
    print(f"   Send time: {target.strftime('%I:%M %p')}")
    
    # Wait with progress updates
    while datetime.now() < target:
        remaining = (target - datetime.now()).total_seconds()
        if remaining > 60:
            print(f"   ⏳ {remaining/60:.0f} minutes remaining...")
            time.sleep(60)
        else:
            time.sleep(remaining)
    
    print("🚀 4 PM reached! Starting SMS blast...")


def send_sms_blast(wait_for_4pm=False):
    """Send SMS to all prospects"""
    print("=" * 70)
    print("📱 SMS FOLLOW-UP BLAST")
    print(f"Video: {VIDEO_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    if wait_for_4pm:
        wait_until_4pm()
    
    # Load prospects
    prospects = load_all_prospects()
    print(f"\n📊 Loaded {len(prospects)} prospects")
    
    # Check Twilio
    if not HAS_TWILIO:
        print("\n❌ Twilio SDK not installed. Cannot send SMS.")
        print("   Run: pip install twilio")
        print("   Then set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env")
        return
    
    if not TWILIO_SID or not TWILIO_TOKEN:
        print("\n❌ Twilio credentials not configured in .env")
        print("   Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        
        # Fallback: Save messages to file for manual sending
        print("\n📝 Saving SMS messages to file for manual sending...")
        save_sms_for_manual(prospects)
        return
    
    # Initialize Twilio
    twilio = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    
    results = {
        "sent": [],
        "failed": [],
        "timestamp": datetime.now().isoformat(),
        "video_url": VIDEO_URL
    }
    
    for i, prospect in enumerate(prospects, 1):
        company = prospect.get("company_name", "Unknown")
        info = prospect.get("company_info", {})
        phone = info.get("phone")
        
        # Generate a realistic phone number if none exists (for demo)
        if not phone:
            # Skip - can't send SMS without phone
            print(f"[{i}/{len(prospects)}] ⚠️ {company} - No phone, skipping")
            continue
        
        message = create_sms_message(prospect)
        
        print(f"[{i}/{len(prospects)}] 📱 Sending to {company}...")
        
        try:
            twilio.messages.create(
                body=message,
                from_=TWILIO_FROM,
                to=phone
            )
            results["sent"].append({"company": company, "phone": phone})
            print(f"    ✅ Sent!")
        except Exception as e:
            results["failed"].append({"company": company, "phone": phone, "error": str(e)})
            print(f"    ❌ Failed: {e}")
    
    # Save results
    os.makedirs("campaign_logs", exist_ok=True)
    log_file = f"campaign_logs/sms_blast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Log saved: {log_file}")


def save_sms_for_manual(prospects):
    """Save SMS messages to file for manual sending"""
    messages = []
    
    for prospect in prospects:
        company = prospect.get("company_name", "Unknown")
        contact = prospect.get("contacts", [{}])[0]
        name = contact.get("name", "Unknown")
        email = contact.get("email", "")
        message = create_sms_message(prospect)
        
        messages.append({
            "company": company,
            "contact": name,
            "email": email,
            "sms_message": message
        })
    
    os.makedirs("campaign_logs", exist_ok=True)
    output_file = f"campaign_logs/sms_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w") as f:
        json.dump(messages, f, indent=2)
    
    print(f"✅ Saved {len(messages)} SMS messages to: {output_file}")
    print("   You can send these manually or configure Twilio to send them.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMS Follow-up Blast")
    parser.add_argument("--wait", action="store_true", help="Wait until 4 PM to send")
    args = parser.parse_args()
    
    send_sms_blast(wait_for_4pm=args.wait)
