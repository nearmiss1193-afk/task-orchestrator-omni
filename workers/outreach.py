"""
MISSION: OUTREACH WORKERS - Hardened Email/SMS/Call Dispatch
All with webhook validation and error checks
"""
import sys
import os

if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT]) # Schedule moved to Railway background_worker.py
def sync_ghl_contacts():
    """
    ZERO-TAX POLLING: Fetches new contacts from GHL every 5 minutes.
    Bypasses $0.01 per webhook tax.
    """
    print("🔄 SYNC: Polling GHL for new contacts...")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    from datetime import datetime, timezone, timedelta

    supabase = get_supabase()
    location_id = os.environ.get("GHL_LOCATION_ID")
    api_token = os.environ.get("GHL_API_TOKEN")

    if not location_id or not api_token:
        print("❌ Sync Error: Missing GHL credentials in Vault")
        return

    # Fetch contacts updated in the last 10 minutes (to ensure overlap)
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit=20"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        contacts = response.json().get("contacts", [])
        print(f"📥 Found {len(contacts)} contacts in GHL.")

        for contact in contacts:
            ghl_id = contact.get("id")
            email = contact.get("email")
            phone = contact.get("phone")
            name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()

            # UPSERT into contacts_master
            # We match by ghl_contact_id to avoid duplicates
            data = {
                "ghl_id": ghl_id,
                "email": email,
                "phone": phone,
                "full_name": name,
                "status": "new", # Default to new for incoming
                "source": "polling_sync",
                "meta": contact
            }
            
            # Using Supabase upsert on ghl_id
            res = supabase.table("contacts_master").upsert(data, on_conflict="ghl_id").execute()
            if res.data:
                print(f"✅ Synced lead: {name} ({ghl_id})")

    except Exception as e:
        print(f"❌ Sync Failed: {e}")

@app.function(image=image, secrets=[VAULT])
def log_consent(lead_id: str, consent_type: str, source: str = "checkout"):
    """
    CONSENT DEFENSE: Records explicit consent for audit trails.
    """
    print(f"⚖️ CONSENT: Logging {consent_type} for Lead {lead_id}...")
    from modules.database.supabase_client import get_supabase
    import datetime

    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead:
        print(f"❌ Error: Lead {lead_id} not found")
        return

    data = {
        "lead_id": lead_id,
        "phone": lead.get("phone"),
        "consent_type": consent_type,
        "source_url": source,
        "ip_address": "recorded", # Proxy for actual IP if available
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    supabase.table("consent_audit_log").insert(data).execute()
    print(f"✅ Consent Recorded for {lead.get('full_name')}")

@app.function(image=image, secrets=[VAULT])
def dispatch_email_logic(lead_id: str):
    """Dispatches email via GHL webhook."""
    print(f"📧 EMAIL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead or not lead.get("ghl_contact_id"):
        print(f"❌ Error: Lead {lead_id} has no GHL ID")
        return False

    hook_url = os.environ.get("GHL_EMAIL_WEBHOOK_URL")
    if not hook_url:
        print("❌ Error: GHL_EMAIL_WEBHOOK_URL missing")
        return False

    # Standardized Webhook Bridge Payload
    payload = {
        "contact_id": lead.get('ghl_contact_id') or lead.get('ghl_id'),
        "first_name": lead.get('full_name', '').split(' ')[0],
        "email": lead.get('email'),
        "subject": "quick question",
        "body": lead.get('ai_strategy', 'hey, saw your site and had a question'),
        "type": "Email"
    }
    
    try:
        requests.post(hook_url, json=payload, timeout=10)
        supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead_id).execute()
        
        supabase.table("outbound_touches").insert({
            "phone": lead.get("phone"),
            "channel": "email",
            "company": lead.get("company_name", "Unknown"),
            "status": "sent"
        }).execute()
        print(f"✅ EMAIL DISPATCHED via Bridge")
        return True
    except Exception as e:
        print(f"❌ EMAIL BRIDGE FAIL: {e}")
        return False
    
    print(f"✅ EMAIL SENT")
    return True

@app.function(image=image, secrets=[VAULT])
def dispatch_sms_logic(lead_id: str, message: str = None):
    """Dispatches SMS via GHL webhook."""
    print(f"📱 SMS DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    hook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not hook_url:
        print("❌ Error: GHL_SMS_WEBHOOK_URL missing")
        return False

    ghl_id = lead.get('ghl_id') or lead.get('ghl_contact_id')
    phone = lead.get('phone', '')
    if phone and not phone.startswith('+'):
        phone = f"+1{phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')}"
    
    # Standardized Webhook Bridge Payload
    payload = {
        "phone": phone,
        "contact_id": ghl_id,
        "first_name": lead.get('full_name', '').split(' ')[0],
        "message": message or "hey, saw your site. had a quick question. you around?",
        "type": "SMS"
    }
    
    try:
        response = requests.post(hook_url, json=payload, timeout=10)
        status = "dispatched" if response.status_code in [200, 201, 202] else f"failed_{response.status_code}"
        print(f"📡 GHL SMS BRIDGE STATUS: {status}")
    except Exception as e:
        status = f"error: {str(e)}"
        print(f"❌ SMS BRIDGE ERROR: {status}")

    supabase.table("contacts_master").update({"status": "outreach_dispatched" if "dispatched" in status else "failed"}).eq("id", lead_id).execute()
    
    supabase.table("outbound_touches").insert({
        "phone": phone,
        "channel": "sms",
        "company": lead.get("company_name", "Unknown"),
        "status": status
    }).execute()
    
    print(f"✅ SMS {status.upper()}")
    return "dispatched" in status

@app.function(image=image, secrets=[VAULT])
def dispatch_call_logic(lead_id: str):
    """Initiates outbound call via Vapi."""
    print(f"📞 CALL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from modules.outbound_dialer import dial_prospect
    import datetime
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    dial_res = dial_prospect(
        phone_number=lead['phone'], 
        company_name=lead.get('company_name', ''),
        assistant_id=os.environ.get("VAPI_ASSISTANT_ID") or "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    )
    
    status = "initiated" if dial_res.get('success') else "failed"
    supabase.table("contacts_master").update({"status": "calling_initiated"}).eq("id", lead_id).execute()
    
    supabase.table("outbound_touches").insert({
        "phone": lead.get("phone"),
        "channel": "call",
        "company": lead.get("company_name", "Unknown"),
        "status": status,
        "payload": {"call_id": dial_res.get("call_id")}
    }).execute()
    
    print(f"✅ CALL {status.upper()}")
    return True
@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"))
def auto_outreach_loop():
    """
    AUTONOMOUS OUTREACH ENGINE:
    - Processes 'new' or 'research_done' leads in batches of 10.
    - Routes to SMS/Email based on business hours and contact info.
    """
    import os
    import requests
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    print("🚀 ENGINE: Starting autonomous outreach cycle...")
    supabase = get_supabase()
    
    # 1. Fetch contactable leads
    try:
        res = supabase.table("contacts_master") \
            .select("*") \
            .in_("status", ["new", "research_done"]) \
            .limit(10) \
            .execute()
        leads = res.data
    except Exception as e:
        print(f"❌ ENGINE: lead fetch error: {e}")
        return
    
    if not leads:
        print("😴 ENGINE: No leads ready for outreach.")
        return

    print(f"📈 ENGINE: Processing {len(leads)} leads...")
    
    for lead in leads:
        lead_id = lead['id']
        email = lead.get('email')
        phone = lead.get('phone')
        
        # Priority 1: SMS (if business hours)
        # EST Business Hours: 8 AM - 6 PM
        est = timezone(timedelta(hours=-5))
        now_est = datetime.now(est)
        is_sms_hours = 8 <= now_est.hour < 18 and now_est.weekday() < 6
        
        if phone and is_sms_hours:
            print(f"📱 Route -> SMS: {phone}")
            try:
                # Use direct function call to avoid spawn overhead during scaling
                dispatch_sms_logic.local(lead_id)
            except Exception as e:
                print(f"❌ SMS Failed for {lead_id}: {e}")
            continue
            
        # Priority 2: Email (24/7)
        if email:
            print(f"📧 Route -> Email: {email}")
            try:
                dispatch_email_logic.local(lead_id)
            except Exception as e:
                print(f"❌ Email Failed for {lead_id}: {e}")
            continue
            
        print(f"⚠️ Skipping Lead {lead_id}: No contact path.")
        supabase.table("contacts_master").update({"status": "no_contact_info"}).eq("id", lead_id).execute()

    print("✅ ENGINE: Outreach cycle complete.")
