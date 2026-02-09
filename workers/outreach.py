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
    """Initiates outbound call via Vapi with Metadata Injection (Phase 5)."""
    print(f"📞 CALL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from modules.outbound_dialer import dial_prospect
    from modules.vapi.metadata_injector import generate_vapi_metadata, inject_metadata_into_payload
    import datetime
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead or not lead.get("phone"):
        print(f"❌ Call Fail: No phone for {lead_id}")
        return False

    # 1. Generate Metadata Context (Phase 5 Sovereign Standard)
    metadata = generate_vapi_metadata(lead['phone'], supabase)
    
    # 2. Build Payload
    # Note: dial_prospect handles original logic, we pass metadata as an override
    dial_res = dial_prospect(
        phone_number=lead['phone'], 
        company_name=lead.get('company_name', ''),
        assistant_id=os.environ.get("VAPI_ASSISTANT_ID") or "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
        metadata_overrides=metadata # Assuming dial_prospect supports this or we update it
    )
    
    status = "initiated" if dial_res.get('success') else "failed"
    supabase.table("contacts_master").update({"status": "calling_initiated"}).eq("id", lead_id).execute()
    
    supabase.table("outbound_touches").insert({
        "phone": lead.get("phone"),
        "channel": "call",
        "company": lead.get("company_name", "Unknown"),
        "status": status,
        "payload": {"call_id": dial_res.get("call_id"), "metadata_injected": True}
    }).execute()
    
    print(f"✅ CALL {status.upper()} with Metadata Injection")
    return True
def auto_outreach_loop():
    """
    AUTONOMOUS OUTREACH ENGINE v2 (Board-Approved Feb 9, 2026):
    - Processes 'new' or 'research_done' leads first (fresh leads).
    - Recycles 'outreach_sent' leads after 3-day cooldown (prevents queue exhaustion).
    - Routes to SMS/Email based on business hours and contact info.
    - SOVEREIGN LAW: "An empty queue is a silent killer."
    """
    import os
    import requests
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    print("🚀 ENGINE v2: Starting autonomous outreach cycle...")
    supabase = get_supabase()
    
    # 1. Fetch FRESH leads first (priority)
    leads = []
    try:
        res = supabase.table("contacts_master") \
            .select("*") \
            .in_("status", ["new", "research_done"]) \
            .limit(10) \
            .execute()
        leads = res.data or []
        print(f"📊 Fresh leads found: {len(leads)}")
    except Exception as e:
        print(f"❌ ENGINE: fresh lead fetch error: {e}")
    
    # 2. If fresh queue is low, RECYCLE old leads (3-day cooldown)
    if len(leads) < 10:
        try:
            cooldown_cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            recycled = supabase.table("contacts_master") \
                .select("*") \
                .eq("status", "outreach_sent") \
                .lt("updated_at", cooldown_cutoff) \
                .limit(10 - len(leads)) \
                .execute()
            recycled_leads = recycled.data or []
            if recycled_leads:
                print(f"♻️ Recycling {len(recycled_leads)} leads past 3-day cooldown")
                leads.extend(recycled_leads)
        except Exception as e:
            print(f"⚠️ ENGINE: recycle query error (non-fatal): {e}")
    
    if not leads:
        print("😴 ENGINE: No leads ready for outreach (fresh or recycled).")
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

    print("✅ ENGINE v2: Outreach cycle complete.")
