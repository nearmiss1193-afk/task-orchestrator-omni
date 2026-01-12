"""
🔥 TURBO BLITZ - Maximum outreach before business hours end
East Coast Time: Hitting leads HARD before 6 PM
"""
import os
import sys
import json
import requests
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
load_dotenv()

# Credentials
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/97b8fc1e-d1cc-4d3a-a123-abc123456789"

def validate_phone(phone_str):
    if not phone_str:
        return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10:
        return False, None
    exchange = cleaned[-7:-4] if len(cleaned) >= 7 else ""
    if exchange == "555":  # Fake numbers
        return False, None
    return True, f"+1{cleaned[-10:]}"

def get_leads_to_contact(limit=25):
    """Get leads that haven't been contacted yet"""
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get leads that need outreach
    result = client.table("leads").select("*")\
        .in_("status", ["new", "enriched", "processing_email", "needs_enrichment"])\
        .limit(limit)\
        .execute()
    
    leads = []
    for lead in result.data:
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        if not meta or not isinstance(meta, dict):
            meta = {}
        
        # Get best phone
        phone = None
        for p in [meta.get("enriched_phone"), lead.get("phone"), meta.get("phone")]:
            is_valid, cleaned = validate_phone(p)
            if is_valid:
                phone = cleaned
                break
        
        # Get email
        email = meta.get("enriched_email") or meta.get("email") or lead.get("email")
        
        if phone or email:
            leads.append({
                "id": lead["id"],
                "company": lead.get("company_name", "Business"),
                "phone": phone,
                "email": email,
                "status": lead.get("status")
            })
    
    return leads, client

def make_call(phone, company):
    """Outbound call via Vapi"""
    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={
                "Authorization": f"Bearer {VAPI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": SARAH_ASSISTANT_ID,
                "customer": {"number": phone, "name": company}
            },
            timeout=30
        )
        return resp.status_code in [200, 201], resp.json() if resp.status_code in [200, 201] else resp.text
    except Exception as e:
        return False, str(e)

def send_sms(phone, company):
    """SMS via GHL"""
    try:
        msg = f"Hi! This is Daniel from AI Service Co. I help businesses like {company} automate phone calls with AI. Worth a quick chat? 352-758-5336"
        resp = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": msg}, timeout=15)
        return resp.status_code in [200, 201]
    except:
        return False

def send_email(email, company):
    """Email via Resend (for system notifications)"""
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key or not email or "N/A" in str(email):
        return False
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}"},
            json={
                "from": "Daniel @ AI Service Co <daniel@aiserviceco.com>",
                "to": [email],
                "subject": f"Quick question for {company}",
                "html": f"<p>Hi!</p><p>I noticed {company} might benefit from AI phone automation for appointment setting, customer service, and lead qualification.</p><p>Would you be open to a quick 5-minute call this week?</p><p>Best,<br>Daniel<br>AI Service Co<br>(352) 758-5336</p>"
            },
            timeout=15
        )
        return resp.status_code in [200, 201]
    except:
        return False

def update_lead_status(client, lead_id, new_status):
    """Update lead status in Supabase"""
    try:
        client.table("leads").update({"status": new_status}).eq("id", lead_id).execute()
    except:
        pass

def contact_lead(lead, client):
    """Contact a single lead with all channels"""
    results = {"call": False, "sms": False, "email": False}
    company = lead["company"]
    
    if lead["phone"]:
        results["call"], _ = make_call(lead["phone"], company)
        if results["call"]:
            time.sleep(2)  # Brief pause between calls
        results["sms"] = send_sms(lead["phone"], company)
    
    if lead["email"]:
        results["email"] = send_email(lead["email"], company)
    
    # Update status
    if any(results.values()):
        update_lead_status(client, lead["id"], "contacted")
    
    return lead, results

def main():
    print("="*60)
    print("🔥 TURBO BLITZ MODE - MAXIMUM OUTREACH 🔥")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%I:%M %p ET')} - Let's HUSTLE!")
    print()
    
    # Get leads
    leads, client = get_leads_to_contact(limit=20)
    print(f"📋 Found {len(leads)} leads to contact")
    print()
    
    if not leads:
        print("⚠️ No leads available - need to run prospector!")
        return
    
    # Stats
    stats = {"calls": 0, "sms": 0, "emails": 0, "total": 0}
    
    # Contact each lead
    for i, lead in enumerate(leads, 1):
        company = str(lead.get('company') or 'Business')[:35]
        phone = lead.get('phone') or 'No phone'
        email = str(lead.get('email') or 'No email')[:25]
        print(f"[{i}/{len(leads)}] {company}")
        print(f"         📞 {phone} | 📧 {email}")
        
        _, results = contact_lead(lead, client)
        
        if results["call"]:
            stats["calls"] += 1
            print(f"         ✅ CALL initiated")
        if results["sms"]:
            stats["sms"] += 1
            print(f"         ✅ SMS sent")
        if results["email"]:
            stats["emails"] += 1
            print(f"         ✅ EMAIL sent")
        
        stats["total"] += 1
        print()
        
        # Small delay to not overwhelm
        time.sleep(1)
    
    print("="*60)
    print("🏁 BLITZ COMPLETE!")
    print("="*60)
    print(f"📞 Calls: {stats['calls']}")
    print(f"💬 SMS: {stats['sms']}")
    print(f"📧 Emails: {stats['emails']}")
    print(f"📊 Total Leads Contacted: {stats['total']}")
    print("="*60)

if __name__ == "__main__":
    main()
