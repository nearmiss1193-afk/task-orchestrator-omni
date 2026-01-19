#!/usr/bin/env python3
"""
EAST COAST SMS OUTREACH - 15 NEW leads NOW
Uses GHL webhook to send SMS to leads marked as NEW
"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Get 15 NEW leads with phone numbers
print("📋 Getting 15 NEW leads from Supabase...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/leads?status=eq.new&phone=not.is.null&limit=15",
    headers=headers
)

if not r.ok:
    print(f"ERROR: {r.status_code} - {r.text}")
    exit(1)

leads = r.json()
print(f"Found {len(leads)} NEW leads with phones\n")

if len(leads) == 0:
    print("No NEW leads found. Run reset_for_outreach.py first.")
    exit(0)

sent = 0
failed = 0

for lead in leads:
    phone = lead.get('phone')
    company = lead.get('company_name', 'your company')
    lead_id = lead.get('id')
    
    if not phone:
        continue
    
    # Clean phone
    phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '')
    if not phone_clean.startswith('+'):
        digits = ''.join(c for c in phone_clean if c.isdigit())
        phone_clean = f"+1{digits}" if len(digits) == 10 else f"+{digits}"
    
    # AI-friendly opener message
    message = f"Hi! Noticed {company} might be missing calls after-hours. Our AI answers 24/7 and books appointments. Worth a quick chat? Reply STOP to opt out"
    
    print(f"📱 {company} - {phone_clean}")
    
    try:
        sms_r = requests.post(GHL_SMS_WEBHOOK, json={
            "phone": phone_clean,
            "message": message,
            "company": company,
            "lead_id": lead_id
        }, timeout=30)
        
        if sms_r.status_code in [200, 201]:
            print(f"   ✅ Sent!")
            sent += 1
            
            # Mark lead as contacted
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
                headers=headers,
                json={"status": "contacted"}
            )
            
            # Log event
            requests.post(
                f"{SUPABASE_URL}/rest/v1/event_log_v2",
                headers=headers,
                json={
                    "type": "sms.outbound.sent",
                    "entity_type": "lead",
                    "entity_id": lead_id,
                    "metadata": {"phone": phone_clean, "company": company}
                }
            )
        else:
            print(f"   ❌ Failed: {sms_r.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed += 1

print(f"\n{'='*50}")
print(f"✅ CAMPAIGN COMPLETE: {sent} sent, {failed} failed")
print(f"{'='*50}")
print("\nMonitor replies at: https://www.aiserviceco.com/dashboard.html")
