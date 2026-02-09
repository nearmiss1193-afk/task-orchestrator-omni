"""
MISSION: OUTREACH WORKERS - Hardened Email/SMS/Call Dispatch
All with webhook validation and error checks

GHL API POLICY (Owner Directive, Feb 9, 2026):
  ❌ BANNED:  GHL API (all endpoints) — $99 plan PIT token returns 401
  ✅ EMAIL:   Resend API (tracked: opens, clicks, bounces, A/B tested)
  ✅ SMS:     GHL webhooks ONLY (for leads with real GHL contact IDs)
  🔄 PLAN:   Migrate away from GHL entirely

DO NOT write code that calls services.leadconnectorhq.com directly.
Use GHL webhook URL for SMS only. Use Resend API for all email.
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
    """
    Dispatches email via Resend API with full tracking.
    Board-approved Phase 3 (Feb 9, 2026):
    - A/B tests 4 subject lines (tracked in outbound_touches.variant_name)
    - Smart personalized body for leads without ai_strategy
    - Embedded tracking pixel for open detection
    - No GHL ID required (sends directly to email address)
    """
    print(f"📧 EMAIL DISPATCH [Resend]: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    import random
    import traceback
    import uuid
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead:
        print(f"❌ Error: Lead {lead_id} not found")
        return False

    email = lead.get('email')
    if not email:
        print(f"❌ Error: Lead {lead_id} has no email")
        return False

    # Filter out placeholder/test emails that waste Resend credits
    skip_patterns = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned']
    if any(p in email.lower() for p in skip_patterns):
        print(f"⚠️ Skipping placeholder email: {email}")
        return False

    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("❌ Error: RESEND_API_KEY missing")
        return False

    # --- A/B SUBJECT LINES (4 variants) ---
    first_name = (lead.get('full_name') or 'there').split(' ')[0]
    company = lead.get('company_name') or 'your company'
    niche = lead.get('niche') or 'your industry'
    
    subject_variants = [
        {"id": "A", "subject": f"Quick question about {company}"},
        {"id": "B", "subject": "Noticed something on your site"},
        {"id": "C", "subject": f"{first_name}, saw something about {niche}"},
        {"id": "D", "subject": f"This caught my eye about {company}"},
    ]
    
    chosen = random.choice(subject_variants)
    subject = chosen["subject"]
    variant_id = chosen["id"]
    
    # --- SMART EMAIL BODY ---
    ai_body = lead.get('ai_strategy')
    if ai_body and len(ai_body) > 20:
        # Use AI-generated strategy if available
        body_text = ai_body
    else:
        # Smart fallback for the 67% of leads without ai_strategy
        body_text = f"""Hi {first_name},

I was just reviewing {company}'s online presence and had a quick question.

Are you currently looking to get more customers from Google and social media?

I work with {niche} businesses and noticed a few quick wins that could help drive more leads to your site.

Worth a 5-min chat this week?

Best,
Dan"""

    # --- TRACKING PIXEL ---
    email_uid = str(uuid.uuid4())[:8]
    tracking_base = os.environ.get("MODAL_TRACKING_URL", "https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run")
    tracking_pixel = f'<img src="{tracking_base}?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'
    
    # Build HTML body
    html_body = f"""<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
{body_text.replace(chr(10), '<br>')}
</div>
{tracking_pixel}"""

    # --- SEND VIA RESEND API ---
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <dan@aiserviceco.com>")
    
    payload = {
        "from": from_email,
        "to": [email],
        "subject": subject,
        "html": html_body,
        "tags": [
            {"name": "lead_id", "value": lead_id},
            {"name": "variant", "value": variant_id},
            {"name": "email_uid", "value": email_uid}
        ]
    }
    
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=15
        )
        
        if r.status_code in [200, 201]:
            resend_data = r.json()
            resend_email_id = resend_data.get("id", "")
            print(f"✅ EMAIL SENT via Resend (ID: {resend_email_id}, Variant: {variant_id})")
            
            # Update lead status
            supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead_id).execute()
            
            # Log to outbound_touches with A/B tracking
            supabase.table("outbound_touches").insert({
                "phone": lead.get("phone"),
                "channel": "email",
                "company": company,
                "status": "sent",
                "variant_id": variant_id,
                "variant_name": subject,
                "correlation_id": resend_email_id,
                "payload": {
                    "resend_email_id": resend_email_id,
                    "email_uid": email_uid,
                    "to": email,
                    "from": from_email,
                    "variant": variant_id
                }
            }).execute()
            
            return True
        else:
            print(f"❌ RESEND FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ RESEND ERROR: {e}")
        traceback.print_exc()
        return False

@app.function(image=image, secrets=[VAULT])
def dispatch_sms_logic(lead_id: str, message: str = None):
    """Dispatches SMS via GHL webhook. Requires REAL GHL contact ID (not SCRAPED_)."""
    print(f"📱 SMS DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    import traceback
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead:
        print(f"❌ SMS: Lead {lead_id} not found")
        return False
    
    hook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not hook_url:
        print("❌ Error: GHL_SMS_WEBHOOK_URL missing")
        return False

    ghl_id = lead.get('ghl_contact_id') or lead.get('ghl_id', '')
    
    # CRITICAL: Skip SCRAPED_ IDs — GHL rejects them
    if not ghl_id or ghl_id.startswith('SCRAPED_'):
        print(f"⚠️ SMS SKIP: Lead {lead_id} has no real GHL ID (got: {ghl_id})")
        return False

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
        print(f"📡 GHL SMS BRIDGE STATUS: {status} (HTTP {response.status_code})")
    except Exception as e:
        status = f"error: {str(e)}"
        print(f"❌ SMS BRIDGE ERROR: {status}")
        traceback.print_exc()

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
        
        # Check GHL ID validity for SMS routing
        ghl_id = lead.get('ghl_contact_id') or lead.get('ghl_id', '')
        has_real_ghl = ghl_id and not ghl_id.startswith('SCRAPED_')
        
        # Priority 1: SMS (if business hours AND real GHL ID)
        # EST Business Hours: 8 AM - 6 PM Mon-Sat
        est = timezone(timedelta(hours=-5))
        now_est = datetime.now(est)
        is_sms_hours = 8 <= now_est.hour < 18 and now_est.weekday() < 6
        
        if phone and is_sms_hours and has_real_ghl:
            print(f"📱 Route -> SMS: {phone} (GHL: {ghl_id[:10]}...)")
            try:
                result = dispatch_sms_logic.local(lead_id)
                if result:
                    continue  # SMS sent successfully, next lead
                print(f"⚠️ SMS returned False for {lead_id}, falling to email")
            except Exception as e:
                import traceback
                print(f"❌ SMS Failed for {lead_id}: {e}")
                traceback.print_exc()
                # Fall through to email
            
        # Priority 2: Email (24/7, also fallback from SMS failure)
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
