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
import re
from core.image_config import image, VAULT
from core.apps import engine_app as app

BOOKING_LINK = "https://links.aiserviceco.com/widget/booking/YWQcHuXXznQEQa7LAWeB"
DAN_PHONE = "+13529368152"

def is_valid_email(email: str) -> bool:
    """Basic email validation to prevent bounces from bad prospector data."""
    if not email or not isinstance(email, str):
        return False
    email = email.strip().lower()
    # Must have @ and domain
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    # Skip known bad patterns
    bad_patterns = [
        'placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com',
        'unassigned', 'noreply', 'no-reply', 'wixpress', 'squarespace',
        'sentry.io', 'mailinator', 'tempmail', 'throwaway', 'guerrilla',
        'yopmail', 'sharklasers', 'grr.la', 'dispostable'
    ]
    if any(p in email for p in bad_patterns):
        return False
    # Skip role-based addresses (high bounce)
    role_prefixes = ['info@', 'admin@', 'support@', 'contact@', 'sales@', 'hello@', 'office@']
    if any(email.startswith(p) for p in role_prefixes):
        return False
    return True

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

    # Validate email before sending (prevents bounces)
    if not is_valid_email(email):
        print(f"⚠️ Skipping invalid email: {email}")
        supabase.table("contacts_master").update({"status": "bad_email"}).eq("id", lead_id).execute()
        return False

    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("Error: RESEND_API_KEY missing")
        return False

    # --- LEAD INFO HARDENING (Anti-"None" Protocol - Aggressive v2) ---
    def is_bad_value(val):
        if not val: return True
        v = str(val).strip().lower()
        if v in ['none', 'none none', 'null', 'undefined', '[none]', 'n/a']: return True
        # If it contains "none" and is very short, it's likely a placeholder
        if 'none' in v and len(v) < 10: return True
        return False

    raw_full_name = lead.get('full_name')
    if is_bad_value(raw_full_name):
        full_name = ''
    else:
        full_name = str(raw_full_name).strip()

    raw_company = lead.get('company_name')
    if is_bad_value(raw_company):
        company = full_name if full_name else 'your business'
    else:
        company = str(raw_company).strip()
        
    raw_niche = lead.get('niche')
    if is_bad_value(raw_niche):
        niche = 'local'
    else:
        niche = str(raw_niche).strip()

    source = lead.get('source', '')
    city = lead.get('city') or lead.get('location') or ''
    
    # Smart possessive: "Guys'" not "Guys's"
    def smart_possessive(name):
        if name.lower().endswith(('s', 'z')):
            return f"{name}'"
        return f"{name}'s"
    
    # Smart greeting: detect if full_name is a person name vs business name
    biz_keywords = ['llc', 'inc', 'co', 'corp', 'hvac', 'plumbing', 'electric', 
                    'roofing', 'pest', 'air', 'repair', 'service', 'cleaning',
                    'landscap', 'construction', 'painting', 'restoration', 'guys',
                    'pros', 'team', 'group', 'academy', 'church', 'society',
                    'partners', 'solutions', 'systems', 'brand', 'design']
    name_lower = full_name.lower()
    is_business_name = any(kw in name_lower for kw in biz_keywords) or len(full_name.split()) > 3 or not full_name
    
    if is_business_name:
        first_name = 'there'
    else:
        first_name = full_name.split(' ')[0]
    
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
            {"id": "LF_C", "subject": f"Noticed {smart_possessive(company)} listing"},
            {"id": "LF_D", "subject": f"Quick tip for {smart_possessive(company)} Google presence"},
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

Just reply to this email, text me at (352) 936-8152, or grab 15 min on my calendar:
{BOOKING_LINK}

- Dan, Lakeland Finds"""
        
        from_email = os.environ.get("LAKELAND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
    elif source == 'hiring_trigger':
        # --- HIRING TRIGGER TEMPLATE (Maya as Labor Solution) ---
        subject_variants = [
            {"id": "HT_A", "subject": f"Question about your receptionist role at {company}"},
            {"id": "HT_B", "subject": f"Regarding the hiring for {company}"},
            {"id": "HT_C", "subject": f"Saw you're looking for help at {company}"},
        ]
        
        body_text = f"""Hi {first_name},
        
Saw your posting on Indeed for a new receptionist at {company}.

While you look for the right person, I wanted to see if you'd be open to a faster solution for your after-hours and overflow calls.

We've been helping Lakeland businesses handle 100% of their missed calls and appointment booking using a specialized AI Receptionist (her name is Maya). She never misses a call, speaks perfect English, and integrates directly with your calendar.

She's ready to start today — and Dan can walk you through how it would work for {company} specifically.

Would you be open to a 2-minute demo? Just reply here or pick a time:
{BOOKING_LINK}

Best,
Dan"""
        from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
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
            # Enhanced generic template — used for leads WITHOUT a website URL
            location_line = f" in {city}" if city else ""
            body_text = f"""Hi {first_name},

I was looking at {niche} businesses{location_line} and came across {company}.

I help businesses like yours get more calls and leads from Google without spending a dime on ads — usually within the first 30 days.

Here's what I typically find for {niche} businesses:
• Their Google Business Profile is missing 3-4 easy optimizations
• Their website isn't showing up for the searches their customers actually make
• They're leaving money on the table with no automated follow-up

Would a quick 15-min call be worth it this week? Grab a time here:
{BOOKING_LINK}

Or just reply — happy to share what I'd do specifically for {company}.

Best,
Dan"""
        
        from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
    
    # --- CAMPAIGN TRIAGE HALT & ROUTING CHECK ---
    active_variants = []
    try:
        all_states = supabase.table("system_state").select("key, value").like("key", "campaign_%_status").execute()
        paused_set = {r["key"].replace("campaign_", "").replace("_status", "") for r in (all_states.data or []) if r["value"] == "paused"}
        
        for v in subject_variants:
            if v["id"] not in paused_set:
                active_variants.append(v)
    except Exception as e:
        print(f"⚠️ Warning: Could not verify triage status, defaulting to all variants: {e}")
        active_variants = subject_variants

    if not active_variants:
        print(f"⏸️ ABORT EMAIL: All subject variants for this template are HALTED via Campaign Triage Dashboard.")
        return False

    chosen = random.choice(active_variants)
    subject = chosen["subject"]
    variant_id = chosen["id"]
    
    # --- TRACKING PIXEL ---
    email_uid = str(uuid.uuid4())[:8]
    tracking_base = os.environ.get("MODAL_TRACKING_URL", "https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run")
    tracking_pixel = f'<img src="{tracking_base}?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'
    
    # Build HTML body
    video_html = ""
    raw_research = json.loads(lead.get('raw_research') or '{}')
    video_url = raw_research.get('video_teaser_url')
    if video_url:
        # WRAP VIDEO IN TRACKING REDIRECTOR (Conversion Sprint)
        tracking_url = f"https://nearmiss1193-afk--ghl-omni-automation-track-video-view.modal.run?lid={lead_id}&vid_url={video_url}"
        video_html = f"""<p style="margin-top: 20px; padding: 12px; background: #f8fafc; border-left: 4px solid #ef4444; border-radius: 4px;">
        <b>🎬 Quick Video Teaser for {company}:</b><br>
        I made a 10s cinematic preview of your AI visibility audit. Check it out here:<br>
        <a href="{tracking_url}" style="color: #2563eb; font-weight: bold; text-decoration: underline;">Watch Video Teaser →</a>
        </p>"""

    html_body = f"""<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
{body_text.replace(chr(10), '<br>')}
{video_html}
</div>
{tracking_pixel}"""
    
    payload = {
        "from": from_email,
        "reply_to": "owner@aiserviceco.com",
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
                "body": html_body,
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
    ENGINE v5: Link-Based Audit Email (Feb 12, 2026)
    Generates a personalized AI visibility audit, stores results in Supabase,
    and sends email with a LINK to the report page instead of PDF attachment.
    Better deliverability + click tracking + landing page upsell.
    """
    print(f"📊 AUDIT EMAIL DISPATCH (Link-Based): Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from workers.audit_generator import generate_audit_for_lead
    import requests
    import os
    import uuid
    import traceback
    import base64

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

    # Create unique report ID
    report_id = str(uuid.uuid4())[:12]
    company = lead.get('company_name') or lead.get('full_name') or 'your company'
    ar = audit["audit_results"]

    # Upload PDF to Supabase Storage (optional — report page works without it)
    pdf_url = None
    try:
        pdf_bytes = base64.b64decode(audit["pdf_b64"])
        storage_path = f"audits/{report_id}/{audit['pdf_filename']}"
        supabase.storage.from_("audit-pdfs").upload(
            storage_path,
            pdf_bytes,
            {"content-type": "application/pdf"}
        )
        pdf_url = supabase.storage.from_("audit-pdfs").get_public_url(storage_path)
        print(f"📁 PDF uploaded to storage: {storage_path}")
    except Exception as e:
        print(f"⚠️ PDF storage upload failed (non-fatal): {e}")
        # Report page still works — just won't have download link

    # Store audit results in audit_reports table
    try:
        supabase.table("audit_reports").insert({
            "report_id": report_id,
            "lead_id": lead_id,
            "company_name": company,
            "website_url": lead.get("website_url"),
            "audit_results": {
                "pagespeed": ar["pagespeed"],
                "privacy": ar["privacy"],
                "ai_readiness": ar["ai_readiness"],
                "criticals": ar["criticals"],
            },
            "pdf_url": pdf_url,
        }).execute()
        print(f"✅ Audit report stored: report_id={report_id}")
    except Exception as e:
        print(f"⚠️ audit_reports insert failed: {e}")
        # Will fallback to email with inline findings (no link)

    # Build report URL
    report_url = f"https://www.aiserviceco.com/report.html?id={report_id}"

    # Tracking pixel
    email_uid = str(uuid.uuid4())[:8]
    tracking_base = os.environ.get("MODAL_TRACKING_URL", "https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run")
    tracking_pixel = f'<img src="{tracking_base}?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'

    # Build email body WITH LINK (no attachment)
    video_html = ""
    if ar.get("video_teaser_url"):
        # WRAP VIDEO IN TRACKING REDIRECTOR (Conversion Sprint)
        tracking_url = f"https://nearmiss1193-afk--ghl-omni-automation-track-video-view.modal.run?lid={lead_id}&vid_url={ar['video_teaser_url']}"
        video_html = f"""<p style="margin: 24px 0; padding: 16px; background: #0f172a; color: #f8fafc; border-radius: 12px; border: 1px solid #334155;">
        <span style="color: #38bdf8;">🎬 <b>Cinematic Pattern Interrupt:</b></span><br>
        I generated a 10-second 4K preview of what your brand looks like with full AI optimization:<br>
        <a href="{tracking_url}" style="color: #38bdf8; font-weight: bold; text-decoration: underline;">Watch Cinematic Teaser →</a>
        </p>"""

    html_body = f"""<html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; line-height: 1.6;">
<p>Hi {owner},</p>

<p>I ran a quick AI visibility audit on <b>{lead.get('website_url', company)}</b> and found some things worth sharing.</p>

<p><b>Key findings:</b></p>
<ul style="margin: 8px 0;">
<li>Mobile Performance Score: <b>{score_text}</b></li>
<li>Privacy Policy (FDBR Compliance): <b>{privacy_text}</b></li>
<li>AI Lead Capture: <b>{"active" if ar['ai_readiness']["status"] == "good" else "not detected"}</b></li>
</ul>

{privacy_warning}

{video_html}

<p>I put together a full report with detailed results and recommendations:</p>

<p style="text-align: center; margin: 24px 0;">
<a href="{report_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f59e0b, #ef4444); color: #fff; font-weight: bold; text-decoration: none; border-radius: 8px; font-size: 16px;">View Your Full Report →</a>
</p>

<p>Would you have 10 minutes for a quick call this week? I can walk you through the findings and we can fix the most urgent issue right away.</p>

<p>Best,<br>Dan<br><span style="color: #666; font-size: 12px;">AI Service Co. | owner@aiserviceco.com</span></p>
</body></html>"""

    html_body += tracking_pixel

    # Resend payload — NO attachment (link instead)
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
    payload = {
        "from": from_email,
        "reply_to": "owner@aiserviceco.com",
        "to": [email],
        "subject": audit["subject"],
        "html": html_body,
        "tags": [
            {"name": "lead_id", "value": lead_id},
            {"name": "variant", "value": "AUDIT_LINK"},
            {"name": "email_uid", "value": email_uid},
            {"name": "report_id", "value": report_id}
        ]
    }

    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=15  # Smaller payload now (no PDF)
        )

        if r.status_code in [200, 201]:
            resend_data = r.json()
            resend_email_id = resend_data.get("id", "")
            print(f"✅ AUDIT EMAIL SENT (Link-Based) via Resend (ID: {resend_email_id})")
            print(f"   Report: {report_url}")
            print(f"   PageSpeed: {ar['pagespeed'].get('score','N/A')}/100 | Privacy: {ar['privacy']['status']} | Criticals: {ar['criticals']}")

            # Update lead status
            supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead_id).execute()

            # Log to outbound_touches with audit details
            supabase.table("outbound_touches").insert({
                "phone": lead.get("phone"),
                "channel": "email",
                "company": company,
                "status": "sent",
                "variant_id": "AUDIT_LINK",
                "variant_name": audit["subject"],
                "correlation_id": resend_email_id,
                "body": html_body,
                "payload": {
                    "resend_email_id": resend_email_id,
                    "email_uid": email_uid,
                    "to": email,
                    "from": from_email,
                    "type": "audit_email_link",
                    "report_id": report_id,
                    "report_url": report_url,
                    "pagespeed_score": ar['pagespeed'].get('score'),
                    "privacy_status": ar['privacy']['status'],
                    "ai_readiness": ar['ai_readiness']['status'],
                    "criticals": ar['criticals'],
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
def dispatch_sms_logic(lead_id: str, message: str = None, media_url: str = None):
    """
    Dispatches SMS/MMS via GHL webhook.
    Requires REAL GHL contact ID (not SCRAPED_).
    MMS Pivot: Accepts media_url for cinematic pattern interrupts.
    """
    print(f"📱 SMS/MMS DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    import json
    import traceback
    
    supabase = get_supabase()
    lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    
    if not lead:
        print(f"❌ SMS: Lead {lead_id} not found")
        return False
    
    # Check for video teaser if media_url not provided
    if not media_url:
        try:
            raw = json.loads(lead.get('raw_research') or '{}')
            media_url = raw.get('video_teaser_url')
        except: pass

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
    
    # MMS Pivot: Wrap video in tracking (Conversion Sprint)
    final_media_url = media_url
    if media_url:
        final_media_url = f"https://nearmiss1193-afk--ghl-omni-automation-track-video-view.modal.run?lid={lead_id}&vid_url={media_url}"

    # Standardized Webhook Bridge Payload
    payload = {
        "phone": phone,
        "contact_id": ghl_id,
        "first_name": lead.get('full_name', '').split(' ')[0],
        "message": message or "hey, saw your site. had a quick question. i made a 10s video scan of your mobile presence, thought you'd want to see it. you around?",
        "media_url": final_media_url,
        "type": "SMS" if not media_url else "MMS"
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
        "status": status,
        "body": payload["message"],
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
    
    print("🚀 ENGINE v5.0: Starting autonomous outreach cycle (EMAIL + CALLS)...")
    supabase = get_supabase()
    
    # Call budget: max 3 outbound calls per 5-min cycle to control VAPI costs
    calls_this_cycle = 0
    MAX_CALLS_PER_CYCLE = 3
    
    # 1. Fetch FRESH leads first (priority) → Step 1 initial email
    leads = []
    try:
        res = supabase.table("contacts_master") \
            .select("*") \
            .in_("status", ["new", "research_done"]) \
            .limit(15) \
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
        
        # --- NEW: AI DISPATCH ROUTING (Phase 13) ---
        try:
            from modules.dispatch.router import route_lead
            route_lead(lead_id)
            # Re-fetch lead to get assigned_to/niche updates
            lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
        except Exception as e:
            print(f"🚦 Routing Error for {lead_id}: {e}")
            
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
                    res = dispatch_audit_email.local(lead_id)
                    print(f"DEBUG: dispatch_audit_email result: {res}")
                except Exception as e:
                    print(f"❌ Audit Email Failed for {lead_id}: {e}")
                    # Fallback to generic email if audit fails
                    try:
                        print(f"📧 Fallback -> Generic Email for {lead_id}")
                        dispatch_email_logic.local(lead_id)
                    except Exception as e2:
                        print(f"❌ Generic Email also failed for {lead_id}: {e2}")
            else:
                print(f"📧 Route -> Generic Email (Step 1): {email} (no website)")
                try:
                    dispatch_email_logic.local(lead_id)
                except Exception as e:
                    print(f"❌ Email Failed for {lead_id}: {e}")
            
            # Priority 3: OUTBOUND CALL via VAPI (business hours, if phone exists + real GHL ID)
            # Call AFTER email — multi-touch: email + call in same cycle
            # SCRAPED leads get email only — don't burn Vapi credits on unverified numbers
            if phone and is_sms_hours and has_real_ghl and calls_this_cycle < MAX_CALLS_PER_CYCLE:
                print(f"📞 Route -> OUTBOUND CALL: {phone} (Sarah AI via VAPI)")
                try:
                    call_result = dispatch_call_logic.local(lead_id)
                    if call_result:
                        calls_this_cycle += 1
                        print(f"✅ Call initiated ({calls_this_cycle}/{MAX_CALLS_PER_CYCLE} this cycle)")
                    else:
                        print(f"⚠️ Call returned False for {lead_id}")
                except Exception as e:
                    print(f"❌ Call Failed for {lead_id}: {e}")
            
            continue
            
        print(f"⚠️ Skipping Lead {lead_id}: No contact path.")
        supabase.table("contacts_master").update({"status": "no_contact_info"}).eq("id", lead_id).execute()

    # --- PROCESS FOLLOW-UP LEADS (Step 2 or 3) ---
    # Compute business hours once for follow-up call routing
    est = timezone(timedelta(hours=-5))
    now_est = datetime.now(est)
    is_sms_hours = 8 <= now_est.hour < 18 and now_est.weekday() < 6
    
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
        
        # Route follow-up: Step 2 tries CALL first (business hours), then email
        website = lead.get('website_url')
        phone = lead.get('phone')
        
        # Step 2 follow-up: Try call first during business hours (only for verified GHL leads)
        ghl_id = lead.get('ghl_contact_id') or lead.get('ghl_id', '')
        has_real_ghl = ghl_id and not ghl_id.startswith('SCRAPED_')
        if step == 2 and phone and is_sms_hours and has_real_ghl and calls_this_cycle < MAX_CALLS_PER_CYCLE:
            print(f"📞 Route -> FOLLOW-UP CALL (Step 2): {phone} (Sarah AI)")
            try:
                call_result = dispatch_call_logic.local(lead_id)
                if call_result:
                    calls_this_cycle += 1
                    print(f"✅ Follow-up call initiated ({calls_this_cycle}/{MAX_CALLS_PER_CYCLE})")
                    continue  # Call sent, skip email follow-up
            except Exception as e:
                print(f"❌ Follow-up Call Failed for {lead_id}: {e}")
                # Fall through to email follow-up
        
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

    # --- STEP 4: RETARGET CAMPAIGN (Social + Reputation Growth) ---
    # Additive: sends a repositioned email to leads already in the pipeline.
    # Only targets leads that have been touched but NOT yet received a retarget email.
    print("🔄 ENGINE: Step 4 — Retarget Campaign (Social + Reputation Growth)...")
    retarget_sent = 0
    MAX_RETARGET_PER_CYCLE = 5
    
    try:
        # Fetch leads that completed original sequence OR are stuck in outreach_sent
        retarget_pool = supabase.table("contacts_master") \
            .select("id,email,phone") \
            .in_("status", ["outreach_sent", "sequence_complete"]) \
            .limit(20) \
            .execute()
        retarget_candidates = retarget_pool.data or []
        
        if retarget_candidates:
            print(f"🎯 RETARGET: {len(retarget_candidates)} candidates found")
            
            for candidate in retarget_candidates:
                if retarget_sent >= MAX_RETARGET_PER_CYCLE:
                    print(f"⏸️ RETARGET: Hit cycle limit ({MAX_RETARGET_PER_CYCLE})")
                    break
                
                cid = candidate["id"]
                
                # Quick check: skip if already retargeted (check outbound_touches)
                try:
                    check = supabase.table("outbound_touches") \
                        .select("id,payload") \
                        .eq("phone", candidate.get("phone", "")) \
                        .eq("channel", "email") \
                        .execute()
                    already_retargeted = False
                    for t in (check.data or []):
                        p = t.get("payload") or {}
                        if isinstance(p, str):
                            try:
                                import json as jmod
                                p = jmod.loads(p)
                            except:
                                p = {}
                        if p.get("campaign") == "social_reputation":
                            already_retargeted = True
                            break
                    if already_retargeted:
                        continue
                except:
                    pass
                
                try:
                    result = dispatch_retarget_email(cid)
                    if result:
                        retarget_sent += 1
                except Exception as e:
                    print(f"❌ RETARGET dispatch error for {cid}: {e}")
            
            print(f"📊 RETARGET: {retarget_sent} emails sent this cycle")
        else:
            print("💤 RETARGET: No candidates ready for retargeting")
    except Exception as e:
        print(f"❌ RETARGET STEP ERROR: {e}")


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
    
    full_name = lead.get('full_name') or ''
    company = lead.get('company_name') or full_name or 'your company'
    niche = lead.get('niche') or 'local'
    
    # Smart greeting: detect business name vs person name
    biz_keywords = ['llc', 'inc', 'co', 'corp', 'hvac', 'plumbing', 'electric', 
                    'roofing', 'pest', 'air', 'repair', 'service', 'cleaning',
                    'landscap', 'construction', 'painting', 'restoration', 'guys',
                    'pros', 'team', 'group', 'academy', 'church', 'society',
                    'partners', 'solutions', 'systems', 'brand', 'design']
    name_lower = full_name.lower()
    is_business_name = any(kw in name_lower for kw in biz_keywords) or len(full_name.split()) > 3
    if is_business_name or not full_name:
        first_name = 'there'
    else:
        first_name = full_name.split(' ')[0]
    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
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
        "reply_to": "owner@aiserviceco.com",
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


# ========================================================================
# RETARGET CAMPAIGN: SOCIAL PRESENCE + REPUTATION GROWTH
# Additive campaign — runs alongside existing outreach pipeline.
# Targets leads already touched by the original campaign with a new angle.
# ========================================================================

def dispatch_retarget_email(lead_id: str):
    """
    Sends a REPOSITIONED email to leads who already received the original
    AI Receptionist pitch. This email focuses on:
    - Social Inbox Automation (FB/IG/Google DMs)
    - Google Review Growth & Protection
    - Daily Social Posting + Engagement
    - Reputation Repair / Screening

    Tagged with campaign='social_reputation' in outbound_touches for tracking.
    """
    import os, json, random, uuid, traceback, requests
    from datetime import datetime, timezone
    from modules.database.supabase_client import get_supabase
    
    supabase = get_supabase()
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("❌ RETARGET: RESEND_API_KEY missing")
        return False
    
    # Fetch lead
    try:
        lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
    except Exception as e:
        print(f"❌ RETARGET: Lead fetch error for {lead_id}: {e}")
        return False
    
    if not lead:
        print(f"❌ RETARGET: Lead {lead_id} not found")
        return False
    
    email = lead.get("email")
    if not email or not is_valid_email(email):
        print(f"⚠️ RETARGET: No valid email for {lead_id}")
        return False
    
    # Check: don't send retarget if already sent one
    try:
        existing = supabase.table("outbound_touches").select("id").eq("phone", lead.get("phone", "")).eq("channel", "email").execute()
        for touch in (existing.data or []):
            # Check payload for campaign tag
            payload = touch.get("payload") or {}
            if isinstance(payload, str):
                try: payload = json.loads(payload)
                except: payload = {}
            if payload.get("campaign") == "social_reputation":
                print(f"⏭️ RETARGET: Already sent to {lead_id}, skipping")
                return False
    except:
        pass  # If check fails, proceed anyway
    
    # Parse lead data
    raw_full_name = lead.get("full_name") or ""
    company = lead.get("company_name") or raw_full_name or "your business"
    niche = lead.get("niche") or "local service"
    city = lead.get("city") or lead.get("location") or ""
    
    # Smart greeting
    biz_keywords = ['llc', 'inc', 'co', 'corp', 'hvac', 'plumbing', 'electric',
                    'roofing', 'pest', 'air', 'repair', 'service', 'cleaning',
                    'landscap', 'construction', 'painting', 'restoration', 'solar',
                    'pros', 'team', 'group', 'solutions', 'systems']
    name_lower = raw_full_name.lower()
    is_biz = any(kw in name_lower for kw in biz_keywords) or len(raw_full_name.split()) > 3 or not raw_full_name
    first_name = "there" if is_biz else raw_full_name.split(" ")[0]
    
    # Possessive
    def sp(name):
        return f"{name}'" if name.lower().endswith(('s', 'z')) else f"{name}'s"
    
    location_line = f" in {city}" if city else ""
    
    # --- A/B SUBJECT VARIANTS (RT_ prefix for retarget tracking) ---
    subject_variants = [
        {"id": "RT_A", "subject": f"Quick thought about {sp(company)} online presence"},
        {"id": "RT_B", "subject": f"{first_name}, what customers see when they Google you"},
        {"id": "RT_C", "subject": f"Are {sp(company)} social messages being answered?"},
        {"id": "RT_D", "subject": f"The #1 thing {niche} businesses overlook"},
    ]
    
    chosen = random.choice(subject_variants)
    subject = chosen["subject"]
    variant_id = chosen["id"]
    
    # --- EMAIL BODY: Social + Reputation Growth ---
    body_text = f"""Hi {first_name},

I reached out before about {company}, and I wanted to share something I noticed while looking at {niche} businesses{location_line}.

The #1 reason customers choose one {niche} company over another isn't price — it's what they see online first.

Here's what I keep finding:

⭐ Google reviews under 4.5 stars = 50% fewer calls
📱 Social messages (FB/IG/Google) go unanswered for days
📸 No consistent social posting = invisible to younger buyers
🛡️ One bad review without a response can cost 30+ customers

We've been helping businesses like {company} with an AI-driven system that handles all of this:

→ Responds to social messages (FB, IG, Google) in seconds  
→ Automatically requests reviews after every job  
→ Routes unhappy customers to you BEFORE they post publicly  
→ Posts daily industry-specific content to keep you visible  

The result? More 5-star reviews, more trust, more inbound leads.

Would 15 minutes be worth exploring this for {company}? Grab a time:
{BOOKING_LINK}

Or just reply — happy to send an example of what your social presence could look like.

Best,
Dan"""

    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
    
    # Tracking pixel
    email_uid = str(uuid.uuid4())[:8]
    tracking_pixel = f'<img src="https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run?eid={email_uid}&recipient={email}&business={company}" width="1" height="1" style="display:none" />'
    
    html_body = f"""<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
{body_text.replace(chr(10), '<br>')}
</div>
{tracking_pixel}"""
    
    payload = {
        "from": from_email,
        "reply_to": "owner@aiserviceco.com",
        "to": [email],
        "subject": subject,
        "html": html_body,
        "tags": [
            {"name": "lead_id", "value": lead_id},
            {"name": "variant", "value": variant_id},
            {"name": "campaign", "value": "social_reputation"},
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
            print(f"✅ RETARGET EMAIL SENT (ID: {resend_email_id}, Variant: {variant_id}) → {email}")
            
            # Log to outbound_touches with retarget campaign tag
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
                    "variant": variant_id,
                    "campaign": "social_reputation",
                    "sequence": "retarget"
                }
            }).execute()
            
            return True
        else:
            print(f"❌ RETARGET RESEND FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ RETARGET ERROR: {e}")
        traceback.print_exc()
        return False
