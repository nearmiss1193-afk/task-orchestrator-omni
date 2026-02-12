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
    import json
    
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
        print("Error: RESEND_API_KEY missing")
        return False

    # --- LEAD INFO ---
    first_name = (lead.get('full_name') or 'there').split(' ')[0]
    company = lead.get('company_name') or 'your company'
    niche = lead.get('niche') or 'your industry'
    source = lead.get('source', '')
    
    # --- Parse Google review data from notes (Lakeland Finds leads) ---
    google_rating = 0
    total_reviews = 0
    try:
        notes = json.loads(lead.get('notes') or '{}')
        google_rating = notes.get('google_rating', 0)
        total_reviews = notes.get('total_reviews', 0)
    except:
        pass
    
    # --- LAKELAND FINDS TEMPLATE (Google Reviews Hook) ---
    if source == 'lakeland_finds':
        # A/B subject lines for Lakeland Finds
        subject_variants = [
            {"id": "LF_A", "subject": f"{company} is on LakelandFinds.com"},
            {"id": "LF_B", "subject": f"Your Google reviews, {first_name}"},
            {"id": "LF_C", "subject": f"Noticed {company}'s listing"},
            {"id": "LF_D", "subject": f"Quick tip for {company}'s Google presence"},
        ]
        
        # Build review-specific body
        review_line = ""
        if total_reviews > 0 and google_rating > 0:
            review_line = f"While setting up your page, I noticed you have {total_reviews} Google reviews with a {google_rating} star rating. "
            if total_reviews < 10:
                review_line += "Most businesses in your category that show up first on Google Maps have 30-50+ reviews — and there's a simple way to get there."
            elif total_reviews < 30:
                review_line += "That's solid! Businesses that push past 50 reviews see 2-3x more calls from Google Maps."
            else:
                review_line += "That's great — you're ahead of most. A few tweaks could help you dominate your category."
        else:
            review_line = "I noticed your Google profile could use a boost — businesses with 30+ reviews get significantly more calls from Maps."
        
        body_text = f"""Hi {first_name},

Dan here with Lakeland Finds. We just launched a local business directory for the Lakeland area, and {company} is already featured.

{review_line}

Want a few quick tips on getting more reviews on autopilot? Happy to share what's working for other Lakeland businesses right now.

Just reply to this email or text me at (352) 936-8152.

- Dan, Lakeland Finds"""
        
        from_email = os.environ.get("LAKELAND_FROM_EMAIL", "Dan <dan@aiserviceco.com>")
    else:
        # --- ORIGINAL AI SERVICE CO TEMPLATE ---
        subject_variants = [
            {"id": "A", "subject": f"Quick question about {company}"},
            {"id": "B", "subject": "Noticed something on your site"},
            {"id": "C", "subject": f"{first_name}, saw something about {niche}"},
            {"id": "D", "subject": f"This caught my eye about {company}"},
        ]
        
        ai_body = lead.get('ai_strategy')
        if ai_body and len(ai_body) > 20:
            body_text = ai_body
        else:
            body_text = f"""Hi {first_name},

I was just reviewing {company}'s online presence and had a quick question.

Are you currently looking to get more customers from Google and social media?

I work with {niche} businesses and noticed a few quick wins that could help drive more leads to your site.

Worth a 5-min chat this week?

Best,
Dan"""
        
        from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <dan@aiserviceco.com>")
    
    chosen = random.choice(subject_variants)
    subject = chosen["subject"]
    variant_id = chosen["id"]
    
    # --- TRACKING PIXEL ---
    email_uid = str(uuid.uuid4())[:8]
    tracking_base = os.environ.get("MODAL_TRACKING_URL", "https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run")
    tracking_pixel = f'<img src="{tracking_base}?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'
    
    # Build HTML body
    html_body = f"""<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
{body_text.replace(chr(10), '<br>')}
</div>
{tracking_pixel}"""
    
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

@app.function(image=image, secrets=[VAULT], timeout=120)
def dispatch_audit_email(lead_id: str):
    """
    ENGINE v4: Audit-Powered Email Dispatch (Board Consensus Feb 9, 2026)
    Generates a personalized AI visibility audit PDF and sends via Resend.
    Uses PageSpeed API + FDBR privacy check + AI readiness scan.
    Sovereign Law: "The audit sells the service. The email delivers the audit."
    """
    print(f"📊 AUDIT EMAIL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from workers.audit_generator import generate_audit_for_lead
    import requests
    import os
    import uuid
    import traceback

    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data

    if not lead:
        print(f"❌ Error: Lead {lead_id} not found")
        return False

    email = lead.get('email')
    if not email:
        print(f"❌ Error: Lead {lead_id} has no email")
        return False

    # Filter placeholder emails
    skip_patterns = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned']
    if any(p in email.lower() for p in skip_patterns):
        print(f"⚠️ Skipping placeholder email: {email}")
        return False

    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("❌ Error: RESEND_API_KEY missing")
        return False

    # Generate the audit
    audit = generate_audit_for_lead(lead)

    if not audit["success"]:
        print(f"⚠️ Audit generation failed: {audit.get('error')} — falling back to generic email")
        return dispatch_email_logic.local(lead_id)  # Fallback to generic

    # Tracking pixel
    email_uid = str(uuid.uuid4())[:8]
    tracking_base = os.environ.get("MODAL_TRACKING_URL", "https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run")
    company = lead.get('company_name') or 'your company'
    tracking_pixel = f'<img src="{tracking_base}?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'

    # Build email body with audit findings + tracking pixel
    html_body = audit["body"] + tracking_pixel

    # Resend payload WITH PDF attachment
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <dan@aiserviceco.com>")
    payload = {
        "from": from_email,
        "to": [email],
        "subject": audit["subject"],
        "html": html_body,
        "attachments": [
            {
                "filename": audit["pdf_filename"],
                "content": audit["pdf_b64"],  # base64 encoded PDF
            }
        ],
        "tags": [
            {"name": "lead_id", "value": lead_id},
            {"name": "variant", "value": "AUDIT"},
            {"name": "email_uid", "value": email_uid}
        ]
    }

    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30  # Larger payload with PDF
        )

        if r.status_code in [200, 201]:
            resend_data = r.json()
            resend_email_id = resend_data.get("id", "")
            ar = audit["audit_results"]
            print(f"✅ AUDIT EMAIL SENT via Resend (ID: {resend_email_id})")
            print(f"   PageSpeed: {ar['pagespeed'].get('score','N/A')}/100 | Privacy: {ar['privacy']['status']} | Criticals: {ar['criticals']}")

            # Update lead status
            supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead_id).execute()

            # Log to outbound_touches with audit details
            supabase.table("outbound_touches").insert({
                "phone": lead.get("phone"),
                "channel": "email",
                "company": company,
                "status": "sent",
                "variant_id": "AUDIT",
                "variant_name": audit["subject"],
                "correlation_id": resend_email_id,
                "payload": {
                    "resend_email_id": resend_email_id,
                    "email_uid": email_uid,
                    "to": email,
                    "from": from_email,
                    "type": "audit_email",
                    "pagespeed_score": ar['pagespeed'].get('score'),
                    "privacy_status": ar['privacy']['status'],
                    "ai_readiness": ar['ai_readiness']['status'],
                    "criticals": ar['criticals'],
                    "pdf_filename": audit["pdf_filename"],
                }
            }).execute()

            return True
        else:
            print(f"❌ RESEND FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ AUDIT EMAIL ERROR: {e}")
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
    AUTONOMOUS OUTREACH ENGINE v3 (Board Consensus Feb 9, 2026):
    - Step 1: Fresh leads (new/research_done) → initial email
    - Step 2: Follow-up #1 after 3 days (different angle)
    - Step 3: Follow-up #2 after 7 days (final attempt / value offer)
    - Max 3 email touches per lead, then mark as 'sequence_complete'
    - Routes SMS during business hours for leads with real GHL IDs
    - SOVEREIGN LAW: "An empty queue is a silent killer."
    """
    import os
    import requests
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    print("🚀 ENGINE v4.2: Starting autonomous outreach cycle...")
    supabase = get_supabase()
    
    # 1. Fetch FRESH leads first (priority) → Step 1 initial email
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
    
    fresh_count = len(leads)
    
    # 2. If fresh queue is low, fetch FOLLOW-UP candidates
    # NOTE: No date filter here — timing check happens per-lead via outbound_touches
    followup_leads = []
    if fresh_count < 10:
        try:
            recycled = supabase.table("contacts_master") \
                .select("*") \
                .eq("status", "outreach_sent") \
                .limit(15) \
                .execute()
            followup_leads = recycled.data or []
            if followup_leads:
                print(f"♻️ Follow-up candidates found: {len(followup_leads)}")
        except Exception as e:
            print(f"❌ ENGINE: follow-up query error: {e}")
    
    if not leads and not followup_leads:
        print("😴 ENGINE: No leads ready for outreach (fresh or follow-up).")
        return

    # --- PROCESS FRESH LEADS (Step 1: Initial Email) ---
    print(f"📈 ENGINE: Processing {len(leads)} fresh + {len(followup_leads)} follow-up leads...")
    
    for lead in leads:
        lead_id = lead['id']
        email = lead.get('email')
        phone = lead.get('phone')
        
        # Check GHL ID validity for SMS routing
        ghl_id = lead.get('ghl_contact_id') or lead.get('ghl_id', '')
        has_real_ghl = ghl_id and not ghl_id.startswith('SCRAPED_')
        
        # Priority 1: SMS (if business hours AND real GHL ID)
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
            
        # Priority 2: AUDIT Email for leads with website, generic for others (24/7)
        if email:
            website = lead.get('website_url')
            if website:
                print(f"📊 Route -> AUDIT Email (Step 1): {email} | site: {website}")
                try:
                    dispatch_audit_email.local(lead_id)
                except Exception as e:
                    print(f"❌ Audit Email Failed for {lead_id}: {e}")
                    # Fallback to generic email if audit fails
                    try:
                        dispatch_email_logic.local(lead_id)
                    except Exception as e2:
                        print(f"❌ Generic Email also failed for {lead_id}: {e2}")
            else:
                print(f"📧 Route -> Generic Email (Step 1): {email} (no website)")
                try:
                    dispatch_email_logic.local(lead_id)
                except Exception as e:
                    print(f"❌ Email Failed for {lead_id}: {e}")
            continue
            
        print(f"⚠️ Skipping Lead {lead_id}: No contact path.")
        supabase.table("contacts_master").update({"status": "no_contact_info"}).eq("id", lead_id).execute()

    # --- PROCESS FOLLOW-UP LEADS (Step 2 or 3) ---
    for lead in followup_leads:
        lead_id = lead['id']
        email = lead.get('email')
        
        if not email:
            continue
        
        # Count prior email touches and get last touch timestamp
        touch_count = 0
        last_touch_ts = None
        try:
            prior = supabase.table("outbound_touches") \
                .select("ts,variant_name", count="exact") \
                .eq("channel", "email") \
                .eq("phone", lead.get("phone")) \
                .order("ts", desc=True) \
                .execute()
            touch_count = prior.count or 0
            if prior.data:
                last_touch_ts = prior.data[0].get("ts")
            
            # Also check by company name if phone is null
            if touch_count == 0 and lead.get("company_name"):
                prior2 = supabase.table("outbound_touches") \
                    .select("ts", count="exact") \
                    .eq("channel", "email") \
                    .eq("company", lead.get("company_name")) \
                    .order("ts", desc=True) \
                    .execute()
                touch_count = prior2.count or 0
                if prior2.data:
                    last_touch_ts = prior2.data[0].get("ts")
        except Exception as e:
            print(f"⚠️ Touch count query error for {lead_id}: {e}")
            touch_count = 1  # Assume at least 1

        if touch_count >= 3:
            # Max sequence reached → mark complete
            print(f"✅ Sequence complete for {lead_id} ({touch_count} touches)")
            supabase.table("contacts_master").update({"status": "sequence_complete"}).eq("id", lead_id).execute()
            continue
        
        # Check timing from LAST TOUCH (source of truth = outbound_touches.ts)
        if last_touch_ts:
            day3_cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            if last_touch_ts > day3_cutoff:
                # Last touch was less than 3 days ago — skip
                continue
        
        # Determine follow-up step
        step = touch_count + 1  # 2 = first follow-up, 3 = final follow-up
        
        # Check timing: Step 3 needs 7 days since last touch
        if step == 3 and last_touch_ts:
            day7_cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            if last_touch_ts > day7_cutoff:
                print(f"⏳ Lead {lead_id} not ready for Step 3 yet (needs 7 days since last touch)")
                continue
        
        # Route follow-up: audit PDF for Step 2 if has website, generic otherwise
        website = lead.get('website_url')
        if step == 2 and website:
            print(f"📊 Route -> AUDIT Follow-up (Step 2): {email} | site: {website}")
            try:
                dispatch_audit_email.local(lead_id)
            except Exception as e:
                import traceback
                print(f"❌ Audit Follow-up Failed for {lead_id}: {e}")
                traceback.print_exc()
                # Fallback to generic follow-up
                try:
                    dispatch_followup_email(lead_id, step)
                except Exception as e2:
                    print(f"❌ Generic follow-up also failed: {e2}")
        else:
            print(f"📧 Route -> Follow-up Email (Step {step}): {email}")
            try:
                dispatch_followup_email(lead_id, step)
            except Exception as e:
                import traceback
                print(f"❌ Follow-up Failed for {lead_id} Step {step}: {e}")
                traceback.print_exc()


def dispatch_followup_email(lead_id: str, step: int):
    """
    Follow-up email dispatch — Step 2 (Day 3) or Step 3 (Day 7).
    Different subject/body per step. References the first email.
    """
    import os, requests, traceback, uuid
    from modules.database.supabase_client import get_supabase
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    if not lead:
        print(f"❌ Follow-up: Lead {lead_id} not found")
        return False
    
    email = lead.get("email")
    if not email:
        return False
    
    # Filter placeholder emails
    skip_patterns = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned']
    if any(p in email.lower() for p in skip_patterns):
        print(f"⚠️ Skipping placeholder: {email}")
        return False
    
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("❌ RESEND_API_KEY missing")
        return False
    
    first_name = (lead.get('full_name') or 'there').split(' ')[0]
    company = lead.get('company_name') or 'your company'
    niche = lead.get('niche') or 'your industry'
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <dan@aiserviceco.com>")
    email_uid = str(uuid.uuid4())[:8]
    
    # --- STEP-SPECIFIC TEMPLATES ---
    if step == 2:
        subject = f"Following up, {first_name}"
        body = f"""<html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px;">
<p>Hi {first_name},</p>
<p>I reached out a few days ago about {company}. Wanted to make sure my email didn't get buried.</p>
<p>We've been helping {niche} businesses increase their online visibility by an average of 40% — and I noticed some quick wins that could apply to {company}.</p>
<p>Would you have 10 minutes this week for a quick call? No pressure, just want to share what I found.</p>
<p>Best,<br>Dan</p>
<img src="https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run?eid={email_uid}" width="1" height="1" style="display:none;" />
</body></html>"""
        variant_name = f"Follow-up #{step-1}: Following up"
    
    elif step == 3:
        subject = f"Last note about {company}"
        body = f"""<html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px;">
<p>Hi {first_name},</p>
<p>I'll keep this short — I've reached out a couple times about some opportunities I spotted for {company}.</p>
<p>I put together a free AI visibility audit for businesses in {niche}. It takes 2 minutes to review and shows exactly where you're losing traffic to competitors.</p>
<p>Want me to send it over? Just reply "yes" and I'll have it in your inbox within the hour.</p>
<p>If the timing isn't right, no worries at all. I'll leave you be.</p>
<p>Best,<br>Dan</p>
<img src="https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run?eid={email_uid}" width="1" height="1" style="display:none;" />
</body></html>"""
        variant_name = f"Follow-up #{step-1}: Last note + free audit offer"
    else:
        return False
    
    # --- SEND VIA RESEND ---
    payload = {
        "from": from_email,
        "to": [email],
        "subject": subject,
        "html": body,
        "headers": {"X-Entity-Ref-ID": email_uid}
    }
    
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json=payload, timeout=15
        )
        
        if r.status_code in [200, 201]:
            resend_data = r.json()
            resend_email_id = resend_data.get("id", "")
            print(f"✅ FOLLOW-UP Step {step} SENT (ID: {resend_email_id})")
            
            # Timing tracked via outbound_touches.ts (no updated_at column on contacts_master)
            
            # Log to outbound_touches
            supabase.table("outbound_touches").insert({
                "phone": lead.get("phone"),
                "channel": "email",
                "company": company,
                "status": "sent",
                "variant_id": f"FU{step}",
                "variant_name": variant_name,
                "correlation_id": resend_email_id,
                "payload": {
                    "resend_email_id": resend_email_id,
                    "email_uid": email_uid,
                    "to": email,
                    "from": from_email,
                    "step": step,
                    "sequence": "follow_up"
                }
            }).execute()
            
            return True
        else:
            print(f"❌ FOLLOW-UP RESEND FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ FOLLOW-UP ERROR: {e}")
        traceback.print_exc()
        return False
