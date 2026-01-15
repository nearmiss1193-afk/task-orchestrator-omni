"""
MULTI-TOUCH OUTREACH WORKFLOW
============================
Automated sequence: Email → SMS → Call

Sequence:
1. Send personalized email
2. Wait 30 min → Send SMS
3. Wait 1 hour → Make outbound call

Usage:
    python multi_touch_outreach.py --count 5    # Process 5 leads
    python multi_touch_outreach.py --lead-id X  # Process specific lead
"""
import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Config
SMS_DELAY_SECONDS = 30 * 60  # 30 minutes (set to 30 for testing)
CALL_DELAY_SECONDS = 60 * 60  # 1 hour (set to 60 for testing)

# For quick testing, use short delays
TEST_MODE = True
if TEST_MODE:
    SMS_DELAY_SECONDS = 30  # 30 seconds for testing
    CALL_DELAY_SECONDS = 60  # 1 minute for testing

# Credentials
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "+18632608351")

SUPA_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase():
    return create_client(SUPA_URL, SUPA_KEY) if SUPA_URL and SUPA_KEY else None


def send_email(to_email: str, company: str, city: str = "") -> bool:
    """Send personalized outreach email"""
    if not RESEND_API_KEY:
        print(f"  [EMAIL] ⚠️ No Resend key")
        return False
    
    subject = f"Quick question for {company}"
    body = f"""Hey there,

I noticed {company} is doing great work in {city or 'your area'}. 

Quick question - how are you handling after-hours calls? Based on similar businesses, you might be missing 20-30% of potential customers who call outside business hours.

We built an AI phone agent that answers 24/7, books appointments, and sounds completely natural.

Worth a quick chat?

- Daniel
AI Service Co
(352) 758-5336
"""

    try:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": "Daniel @ AI Service Co <system@aiserviceco.com>",
                "reply_to": "owner@aiserviceco.com",
                "to": [to_email],
                "subject": subject,
                "html": f"<pre style='font-family:sans-serif;line-height:1.6'>{body}</pre>"
            }
        )
        success = res.status_code in [200, 201]
        print(f"  [EMAIL] {'✅' if success else '❌'} {to_email}")
        return success
    except Exception as e:
        print(f"  [EMAIL] ❌ Error: {e}")
        return False


def send_sms(phone: str, company: str) -> bool:
    """Send follow-up SMS via Twilio API"""
    if not TWILIO_SID or not TWILIO_TOKEN:
        print(f"  [SMS] ⚠️ No Twilio credentials")
        return False
    
    message = f"Hi! Just sent you an email about AI phone agents for {company}. Have a minute to chat? Reply YES or call (352) 758-5336 - Sarah will answer!"
    
    try:
        # Use requests instead of Twilio SDK
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            auth=(TWILIO_SID, TWILIO_TOKEN),
            data={
                "From": TWILIO_FROM,
                "To": phone,
                "Body": message
            }
        )
        success = response.status_code in [200, 201]
        print(f"  [SMS] {'✅' if success else '❌'} Sent to {phone}")
        return success
    except Exception as e:
        print(f"  [SMS] ❌ Error: {e}")
        return False


def make_call(phone: str, company: str, city: str = "") -> bool:
    """Make outbound call using Vapi"""
    from modules.outbound_dialer import dial_prospect
    
    result = dial_prospect(phone, company, city)
    success = result.get("success", False)
    print(f"  [CALL] {'✅' if success else '❌'} {phone}")
    return success


def run_sequence(lead: dict) -> dict:
    """Run full Email→SMS→Call sequence for one lead"""
    company = lead.get("company_name", "Your Company")
    
    # Extract contact info
    meta = lead.get("agent_research", {})
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except:
            meta = {}
    
    email = meta.get("email") or lead.get("email")
    phone = meta.get("phone") or lead.get("phone")
    city = meta.get("city", "")
    
    print(f"\n{'='*50}")
    print(f"📞 SEQUENCE: {company}")
    print(f"   Email: {email or 'None'}")
    print(f"   Phone: {phone or 'None'}")
    print(f"{'='*50}")
    
    results = {"lead_id": lead.get("id"), "company": company, "steps": []}
    sb = get_supabase()
    
    # Step 1: Email
    if email:
        print(f"\n[1/3] Sending EMAIL...")
        email_ok = send_email(email, company, city)
        results["steps"].append({"type": "email", "success": email_ok})
        
        if email_ok and sb:
            sb.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
    else:
        print(f"\n[1/3] SKIP EMAIL (no email address)")
        results["steps"].append({"type": "email", "success": False, "reason": "no email"})
    
    # Step 2: SMS (after delay)
    if phone:
        print(f"\n[2/3] Waiting {SMS_DELAY_SECONDS}s before SMS...")
        time.sleep(SMS_DELAY_SECONDS)
        
        print(f"[2/3] Sending SMS...")
        sms_ok = send_sms(phone, company)
        results["steps"].append({"type": "sms", "success": sms_ok})
    else:
        print(f"\n[2/3] SKIP SMS (no phone)")
        results["steps"].append({"type": "sms", "success": False, "reason": "no phone"})
    
    # Step 3: Call (after delay)
    if phone:
        print(f"\n[3/3] Waiting {CALL_DELAY_SECONDS}s before CALL...")
        time.sleep(CALL_DELAY_SECONDS)
        
        print(f"[3/3] Making CALL...")
        call_ok = make_call(phone, company, city)
        results["steps"].append({"type": "call", "success": call_ok})
        
        if call_ok and sb:
            sb.table("leads").update({
                "status": "called",
                "last_called": datetime.now().isoformat()
            }).eq("id", lead["id"]).execute()
    else:
        print(f"\n[3/3] SKIP CALL (no phone)")
        results["steps"].append({"type": "call", "success": False, "reason": "no phone"})
    
    # Log sequence
    if sb:
        sb.table("system_logs").insert({
            "level": "INFO",
            "event_type": "MULTI_TOUCH_SEQUENCE",
            "message": f"Completed sequence for {company}",
            "metadata": results
        }).execute()
    
    return results


def run_outreach(count: int = 5):
    """Run multi-touch outreach on multiple leads"""
    print("="*60)
    print("MULTI-TOUCH OUTREACH WORKFLOW")
    print(f"Sequence: Email → SMS ({SMS_DELAY_SECONDS}s) → Call ({CALL_DELAY_SECONDS}s)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    sb = get_supabase()
    if not sb:
        print("❌ Database not configured")
        return
    
    # Get leads that haven't been contacted
    result = sb.table("leads").select("*")\
        .in_("status", ["new", "processing_email"])\
        .order("created_at", desc=True)\
        .limit(count)\
        .execute()
    
    leads = result.data
    print(f"\nFound {len(leads)} leads to contact")
    
    all_results = []
    for lead in leads:
        results = run_sequence(lead)
        all_results.append(results)
    
    # Summary
    print("\n" + "="*60)
    print("OUTREACH COMPLETE")
    print("="*60)
    print(f"Leads processed: {len(all_results)}")
    
    success_counts = {"email": 0, "sms": 0, "call": 0}
    for r in all_results:
        for step in r.get("steps", []):
            if step.get("success"):
                success_counts[step["type"]] += 1
    
    print(f"Emails sent: {success_counts['email']}")
    print(f"SMS sent: {success_counts['sms']}")
    print(f"Calls made: {success_counts['call']}")
    
    return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Touch Outreach")
    parser.add_argument("--count", type=int, default=3, help="Number of leads")
    parser.add_argument("--test", action="store_true", help="Use short delays for testing")
    
    args = parser.parse_args()
    
    if not args.test:
        # Use production delays
        SMS_DELAY_SECONDS = 30 * 60  # 30 min
        CALL_DELAY_SECONDS = 60 * 60  # 1 hour
    
    run_outreach(args.count)
