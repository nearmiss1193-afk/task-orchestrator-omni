"""
TURBO MANUS-STYLE CAMPAIGN
Like Manus: Generates individual audit reports, sends email+SMS, every 10 minutes
"""
import os
import sys
import time
import json
import psycopg2
import requests
from datetime import datetime

# Fix Windows console encoding for Unicode characters
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# GHL Webhooks
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/cf2e8a9c-e943-4d78-9f6f-cd66bb9a2e42"

# Vapi for calls
VAPI_KEY = "c23c884d-0008-4b14-ad5d-530e98d0c9da"
VAPI_PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# Canadian area codes (Vapi free numbers can't call these - treated as international)
CANADIAN_AREA_CODES = [
    '204', '226', '236', '249', '250', '289', '306', '343', '365', '367',
    '403', '416', '418', '431', '437', '438', '450', '506', '514', '519',
    '548', '579', '581', '587', '604', '613', '639', '647', '672', '705',
    '709', '778', '780', '782', '807', '819', '825', '867', '873', '902', '905'
]

def is_us_phone(phone):
    """Check if phone number is US (not Canadian) - Vapi free # can only call US"""
    if not phone:
        return False
    # Normalize: remove +1, spaces, dashes, parens
    clean = ''.join(c for c in phone if c.isdigit())
    if clean.startswith('1') and len(clean) == 11:
        clean = clean[1:]  # Remove country code
    if len(clean) != 10:
        return False
    area_code = clean[:3]
    if area_code in CANADIAN_AREA_CODES:
        return False
    return True

# Database
DB_CONFIG = {
    "host": "db.rzcpfwkygdvoshtwxncs.supabase.co",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "Inez11752990@"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def generate_site_audit(website_url):
    """Use SiteAuditor to generate financial loss report"""
    try:
        from modules.sales.site_auditor import SiteAuditor
        auditor = SiteAuditor()
        report = auditor.audit_site(website_url)
        return report
    except Exception as e:
        print(f"   Audit error: {e}")
        return None

def generate_premium_audit(company_name, website, audit_data=None):
    """Generate our own premium HTML audit report - BETTER than Manus"""
    try:
        from premium_audit_generator import generate_premium_report
        url, filepath = generate_premium_report(company_name, website, audit_data=audit_data)
        return url
    except Exception as e:
        print(f"   Premium audit error: {e}")
        # Fallback URL
        return f"https://www.aiserviceco.com/audits/{company_name.replace(' ', '-').lower()}.html"

def send_email(email, company_name, audit_link, missed_revenue=0):
    """Send personalized email via GHL webhook"""
    subject = f"ALERT - {company_name}: We Found ${missed_revenue:,} You're Missing"
    body = f"""Hi,

I ran a free website and phone audit for {company_name}.

**Your Custom Report:** {audit_link}

Key Finding: Our analysis shows you're potentially leaving ${missed_revenue:,}/year on the table due to missed calls and manual scheduling.

I'd love to show you how we can fix this in 15 minutes.

Reply to this email or call (863) 337-3705.

Best,
Sarah
AI Service Co
"""
    try:
        resp = requests.post(GHL_EMAIL_WEBHOOK, json={
            "email": email,
            "subject": subject,
            "body": body
        }, timeout=15)
        return resp.status_code in [200, 201]
    except:
        return False

def send_sms(phone, company_name, audit_link):
    """Send SMS via GHL webhook"""
    msg = f"Hi! I just finished an audit for {company_name} and found some interesting opportunities. Check it out: {audit_link}  Reply for a free 15-min consultation. -Sarah"
    try:
        resp = requests.post(GHL_SMS_WEBHOOK, json={
            "phone": phone,
            "message": msg
        }, timeout=15)
        return resp.status_code in [200, 201]
    except:
        return False

def make_call(phone, company_name):
    """Initiate Vapi call - ONLY for US numbers (free Vapi # can't call international)"""
    if not is_us_phone(phone):
        print(f"   [SKIP] Call skipped - non-US phone: {phone}")
        return False
    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": SARAH_ID,
                "customer": {"number": phone, "name": company_name}
            },
            timeout=30
        )
        return resp.status_code in [200, 201]
    except:
        return False

def process_lead(lead_id, company_name, website, email, phone, city, state):
    """Full Manus-style audit + outreach for one lead"""
    print(f"\n[TARGET] Processing: {company_name}")
    
    # Step 1: Generate Site Audit (our own)
    audit_report = None
    missed_revenue = 144000  # Default estimate
    if website:
        print(f"   Running site audit...")
        audit_report = generate_site_audit(website)
        if audit_report and 'financials' in audit_report:
            missed_revenue = audit_report['financials'].get('total_opportunity', 144000)
    
    # Step 2: Generate Premium Audit Report (our own - better than Manus)
    print(f"   Generating premium audit report...")
    audit_link = generate_premium_audit(company_name, website, audit_data={
        'has_chat': False,
        'has_booking': False,
        'missed_calls_weekly': 12,
        'avg_job_value': 450
    })
    
    # Step 3: Send Email
    email_sent = False
    if email:
        print(f"   Sending email to {email}...")
        email_sent = send_email(email, company_name, audit_link, missed_revenue)
        print(f"   {'[OK]' if email_sent else '[FAIL]'} Email")
    
    # Step 4: Send SMS
    sms_sent = False
    if phone:
        print(f"   Sending SMS to {phone}...")
        sms_sent = send_sms(phone, company_name, audit_link)
        print(f"   {'[OK]' if sms_sent else '[FAIL]'} SMS")
    
    # Step 5: Make Call (ENABLED)
    call_made = False
    if phone:
        print(f"   Calling {phone}...")
        call_made = make_call(phone, company_name)
        print(f"   {'[OK]' if call_made else '[FAIL]'} Call")
    
    # Step 6: Update database - mark as contacted
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE leads SET status = 'contacted' WHERE id = %s", (lead_id,))
    conn.commit()
    cur.close()
    conn.close()
    print(f"   [OK] Database updated")
    
    return {"email": email_sent, "sms": sms_sent, "call": call_made, "audit_link": audit_link}

def run_campaign_cycle():
    """Run one cycle - process up to 5 leads"""
    print(f"\n{'='*50}")
    print(f"[CAMPAIGN] MANUS-STYLE CAMPAIGN CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get leads that need audit + outreach
    cur.execute("""
        SELECT id, company_name, website_url, email, phone, city, state 
        FROM leads 
        WHERE status IN ('new', 'enriched', 'audited')
        AND (email IS NOT NULL OR phone IS NOT NULL)
        LIMIT 5
    """)
    leads = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f"Found {len(leads)} leads to process")
    
    results = {"emails": 0, "sms": 0, "calls": 0}
    
    for lead in leads:
        lead_id, company, website, email, phone, city, state = lead
        result = process_lead(lead_id, company, website, email, phone, city, state)
        if result["email"]: results["emails"] += 1
        if result["sms"]: results["sms"] += 1
        if result["call"]: results["calls"] += 1
        time.sleep(2)  # Rate limit
    
    print(f"\n[STATS] Cycle Complete: {results['emails']} emails, {results['sms']} SMS, {results['calls']} calls")
    return results

def main():
    """Main loop - run every 10 minutes like Manus"""
    print("TURBO MANUS-STYLE CAMPAIGN STARTED")
    print("   Generating audits + Email + SMS every 10 minutes")
    print("   Press Ctrl+C to stop\n")
    
    while True:
        try:
            run_campaign_cycle()
            print(f"\n[WAIT] Next cycle in 10 minutes...")
            time.sleep(600)  # 10 minutes
        except KeyboardInterrupt:
            print("\n[STOP] Campaign stopped by user")
            break
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            print("   Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()

