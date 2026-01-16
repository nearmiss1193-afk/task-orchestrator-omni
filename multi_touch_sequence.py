"""
MULTI-TOUCH NURTURE SEQUENCE - 3-touch outreach system
Touch 1: Immediate (email + SMS)
Touch 2: +24h SMS follow-up
Touch 3: +72h SMS + Email final push
"""
import requests
from datetime import datetime, timedelta
import json

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

RESEND_API_KEY = "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Touch message templates
TOUCH_MESSAGES = {
    1: {
        "sms": "Hi! Your private marketing audit for {company} is ready: {link} - Reply for a free strategy session. -Sarah",
        "email_subject": "[PRIVATE] Marketing Audit for {company}",
        "email_body": """<p>Hi,</p>
<p>I just finished your private marketing audit for <b>{company}</b>.</p>
<p>View it here: <a href="{link}">{link}</a></p>
<p>I found some quick wins that could help you get more leads.</p>
<p>Reply or call (863) 337-3705 if you'd like to discuss.</p>
<p>-Sarah<br>AI Service Co</p>"""
    },
    2: {
        "sms": "Quick follow-up - did you get a chance to review your {company} audit? I can walk you through the key findings in 15 min: {booking_link} -Sarah",
        "email_subject": None,  # No email on Touch 2
        "email_body": None
    },
    3: {
        "sms": "Last chance - your {company} audit expires soon. Book a free 15-min call before it's gone: {booking_link} -Sarah",
        "email_subject": "Final reminder: Your {company} audit",
        "email_body": """<p>Hi,</p>
<p>I wanted to give you one last heads up - your private marketing audit for <b>{company}</b> will expire soon.</p>
<p>If you'd like to review the findings together, I have a few slots open this week:</p>
<p><b><a href="{booking_link}">Book your free 15-minute call →</a></b></p>
<p>No pressure - just want to make sure you don't miss out.</p>
<p>-Sarah</p>"""
    }
}

BOOKING_LINK = "https://link.aiserviceco.com/discovery"


def send_sms(phone: str, message: str) -> bool:
    """Send SMS via GHL"""
    try:
        r = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": message}, timeout=15)
        return r.status_code in [200, 201]
    except:
        return False


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email via Resend"""
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "Sarah <sarah@aiserviceco.com>",
                "to": [to_email],
                "subject": subject,
                "html": body
            },
            timeout=15
        )
        return r.status_code in [200, 201]
    except:
        return False


def get_audit_link(company: str) -> str:
    """Generate audit link for company"""
    slug = company.lower().replace(" ", "-").replace("&", "and").replace(",", "")[:30]
    return f"https://www.aiserviceco.com/audits/{slug}.html"


def execute_touch(lead: dict, touch_num: int) -> dict:
    """Execute a specific touch for a lead"""
    company = lead.get("company_name", "Your Business")
    phone = lead.get("phone")
    email = lead.get("email")
    
    audit_link = get_audit_link(company)
    templates = TOUCH_MESSAGES.get(touch_num, {})
    
    result = {"touch": touch_num, "sms_sent": False, "email_sent": False}
    
    # Send SMS
    if phone and templates.get("sms"):
        msg = templates["sms"].format(
            company=company, 
            link=audit_link, 
            booking_link=BOOKING_LINK
        )
        result["sms_sent"] = send_sms(phone, msg)
    
    # Send Email (Touch 1 and Touch 3 only)
    if email and templates.get("email_subject"):
        subject = templates["email_subject"].format(company=company)
        body = templates["email_body"].format(
            company=company, 
            link=audit_link, 
            booking_link=BOOKING_LINK
        )
        result["email_sent"] = send_email(email, subject, body)
    
    return result


def update_lead_touch(lead_id: str, touch_num: int):
    """Update lead with touch info"""
    now = datetime.utcnow().isoformat() + "Z"
    
    update = {
        "last_touch": touch_num,
        f"touch_{touch_num}_at": now,
        "status": "contacted" if touch_num == 1 else "nurturing"
    }
    
    # Calculate next touch time
    if touch_num == 1:
        update["next_touch_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
    elif touch_num == 2:
        update["next_touch_at"] = (datetime.utcnow() + timedelta(hours=48)).isoformat() + "Z"
    else:
        update["next_touch_at"] = None  # No more touches
    
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS,
        json=update
    )


def get_leads_for_touch(touch_num: int, limit: int = 10) -> list:
    """Get leads ready for a specific touch"""
    now = datetime.utcnow().isoformat() + "Z"
    
    if touch_num == 1:
        # New leads that haven't been touched
        params = {"status": "eq.new", "limit": limit}
    else:
        # Leads where next_touch_at has passed and last_touch is previous touch
        params = {
            "last_touch": f"eq.{touch_num - 1}",
            "next_touch_at": f"lte.{now}",
            "limit": limit
        }
    
    r = requests.get(f"{SUPABASE_URL}/rest/v1/leads", headers=HEADERS, params=params)
    return r.json() if r.status_code == 200 else []


def run_sequence():
    """Run full 3-touch sequence"""
    print("=" * 60)
    print(f"MULTI-TOUCH NURTURE SEQUENCE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    stats = {"touch_1": 0, "touch_2": 0, "touch_3": 0, "emails": 0, "sms": 0}
    
    for touch_num in [1, 2, 3]:
        print(f"\n[TOUCH {touch_num}]")
        leads = get_leads_for_touch(touch_num, limit=5)
        print(f"Found {len(leads)} leads ready for Touch {touch_num}")
        
        for lead in leads:
            company = lead.get("company_name", "Unknown")
            result = execute_touch(lead, touch_num)
            update_lead_touch(lead["id"], touch_num)
            
            if result["sms_sent"]:
                stats["sms"] += 1
            if result["email_sent"]:
                stats["emails"] += 1
            stats[f"touch_{touch_num}"] += 1
            
            print(f"  ✅ {company}: SMS={result['sms_sent']}, Email={result['email_sent']}")
    
    print(f"\n[STATS] Touch 1: {stats['touch_1']}, Touch 2: {stats['touch_2']}, Touch 3: {stats['touch_3']}")
    print(f"[STATS] Total SMS: {stats['sms']}, Total Emails: {stats['emails']}")
    
    return stats


if __name__ == "__main__":
    run_sequence()
