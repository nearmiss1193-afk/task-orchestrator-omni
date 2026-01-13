"""
GET LEADS AND CONTACT THEM NOW
Direct outreach - bypasses swarm issues
"""
import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

# Config
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Supabase
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
sb = create_client(url, key)

print("="*60)
print("🚀 DIRECT OUTREACH LAUNCH")
print("="*60)

# Get all leads
result = sb.table('leads').select('*').execute()
leads = result.data or []

print(f"\n📊 Found {len(leads)} leads in database")

stats = {"emails": 0, "sms": 0, "calls": 0}

for i, lead in enumerate(leads):
    company = lead.get('company_name') or lead.get('full_name') or 'Business Owner'
    email = lead.get('email')
    phone = lead.get('phone')
    website = lead.get('website_url', '')
    status = lead.get('status', 'new')
    
    print(f"\n[{i+1}/{len(leads)}] {company}")
    print(f"   Email: {email}")
    print(f"   Phone: {phone}")
    print(f"   Status: {status}")
    
    # Skip if already contacted
    if status == 'contacted':
        print("   ⏭️ Already contacted - skipping")
        continue
    
    # SEND EMAIL
    if email and '@' in str(email):
        try:
            html_body = f"""
            <p>Hey there,</p>
            <p>I just ran a quick audit on <b>{company}</b> and noticed you might be missing calls after hours.</p>
            <p>Most service businesses lose 20-30 calls per week when they can't pick up. We built an AI that answers 24/7, sounds like a real person, and books jobs while you sleep.</p>
            <p><b>14-Day Free Trial</b> - no credit card needed. Let me know if you want to try it.</p>
            <p>Best,<br>Daniel<br>AI Service Co<br>(352) 758-5336</p>
            """
            resp = requests.post(GHL_EMAIL, json={
                "email": email,
                "from_name": "Daniel",
                "from_email": "daniel@aiserviceco.com",
                "subject": f"Quick question for {company}",
                "html_body": html_body
            }, timeout=15)
            if resp.status_code in [200, 201]:
                stats["emails"] += 1
                print(f"   ✅ EMAIL sent")
            else:
                print(f"   ⚠️ Email status: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Email error: {e}")
    
    time.sleep(1)
    
    # SEND SMS
    if phone:
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if len(clean_phone) >= 10:
            try:
                msg = f"Hi! Daniel here from AI Service Co. Just emailed you about an AI receptionist for {company}. 14-day free trial, no card needed. Interested? 352-758-5336"
                resp = requests.post(GHL_SMS, json={
                    "phone": f"+1{clean_phone[-10:]}",
                    "message": msg
                }, timeout=15)
                if resp.status_code in [200, 201]:
                    stats["sms"] += 1
                    print(f"   ✅ SMS sent")
            except Exception as e:
                print(f"   ❌ SMS error: {e}")
    
    # Update status in DB
    try:
        sb.table('leads').update({"status": "contacted"}).eq('id', lead['id']).execute()
        print(f"   ✅ Status updated to 'contacted'")
    except:
        pass
    
    time.sleep(2)

# Copy to owner
print("\n📧 Sending summary to owner...")
try:
    summary = f"<h2>Outreach Complete</h2><p>Emails: {stats['emails']}<br>SMS: {stats['sms']}<br>Leads processed: {len(leads)}</p>"
    requests.post(GHL_EMAIL, json={
        "email": "owner@aiserviceco.com",
        "from_name": "Swarm Bot",
        "from_email": "system@aiserviceco.com",
        "subject": f"[REPORT] Outreach Complete - {stats['emails']} emails, {stats['sms']} SMS",
        "html_body": summary
    }, timeout=15)
    print("   ✅ Summary sent to owner")
except:
    pass

print("\n" + "="*60)
print(f"RESULTS: Emails: {stats['emails']}, SMS: {stats['sms']}, Calls: {stats['calls']}")
print("="*60)
