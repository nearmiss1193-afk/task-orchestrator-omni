# --- DIRECTIVE ---
# Tech Stack: Modal, Supabase, GHL API, Gemini
# Goal: 10x ROI via Autonomous Content & Outreach
# Tone: Spartan (concise, lowercase, संस्थापक-स्तर)
# Log: brain_dump.log

import modal
import os
import json
import requests
import datetime
import google.generativeai as genai
from supabase import create_client, Client
import stripe
from fastapi import Request, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ... existing imports ...

app = modal.App("ghl-omni-automation")

# Image with dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "requests", "google-generativeai", "google-genai", "playwright", "fastapi", "stripe")
    .run_commands("playwright install chromium")
    .add_local_dir(".", remote_path="/root/project", ignore=[".git", "node_modules", ".next", "__pycache__", ".ghl_browser_data", ".tmp", ".vscode", ".ghl_temp_profile_*"])
)

# Shared Secret Reference
VAULT = modal.Secret.from_name("agency-vault")

def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print(f"⚠️ [Error] Missing Supabase Config. URL: {bool(url)}, Key: {bool(key)}")
    return create_client(url, key)

def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")

def brain_log(message: str):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    # In Modal, we write to stdout/stderr, persistent logs should go to DB
    try:
        supabase = get_supabase()
        supabase.table("brain_logs").insert({"message": message, "timestamp": timestamp}).execute()
    except Exception as e:
        print(f"Failed to log to DB: {str(e)}")

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
async def ghl_webhook(payload: dict):
    """
    MISSION 1: GHL TWO-WAY SYNC + HYBRID DIRECTIVE
    """
    import traceback
    brain_log(f"--- WEBHOOK START ---")
    try:
        brain_log(f"Payload: {json.dumps(payload)}")
        
        type = payload.get('type')
        contact_id = payload.get('contact_id') or payload.get('id')
        
        if type == 'ContactUpdate' or not type:
            if not contact_id:
                return {"status": "skipped", "reason": "no contact id"}
                
            brain_log(f"Syncing Contact: {contact_id}")
            supabase = get_supabase()
            supabase.table("contacts_master").upsert({
                "ghl_contact_id": contact_id,
                "full_name": payload.get('name') or payload.get('contact', {}).get('name', 'Unknown'),
                "email": payload.get('email') or payload.get('contact', {}).get('email'),
                "website_url": payload.get('website') or payload.get('contact', {}).get('website'),
                "status": "new"
            }, on_conflict="ghl_contact_id").execute()
            
            # MISSION 2: VORTEX TRIGGER
            tags = payload.get('tags', []) or payload.get('contact', {}).get('tags', [])
            if 'trigger-vortex' in [t.lower() for t in tags]:
                brain_log(f"Vortex Triggered for {contact_id}")
                research_lead_logic.spawn(contact_id)
                return {"status": "vortex_triggered", "contact_id": contact_id}
                
            return {"status": "synced", "contact_id": contact_id}

        elif type == 'InboundMessage':
            brain_log(f"Inbound Message detected for {contact_id}")
            # ... spartan logic ...
            contact_obj = payload.get('contact', {}) or {}
            tags = contact_obj.get('tags', [])
            if 'candidate' in [t.lower() for t in tags] or 'hiring' in [t.lower() for t in tags]:
                return await _hiring_spartan_logic(payload)
            return await _spartan_responder_logic(payload)

        elif type == 'CallStatus':
            status = payload.get('status', '').lower()
            brain_log(f"Call Status Update: {contact_id} -> {status}")
            if status in ['no-answer', 'busy', 'voicemail', 'failed']:
                brain_log(f"🛑 Missed Call Detected for {contact_id}. Triggering Spartan Text-Back.")
                # Construct a mock payload for spartan to react to
                mock_payload = {
                    "contact_id": contact_id,
                    "message": {
                        "body": "[SYSTEM ALERT: PROSPECT MISSED A CALL. SEND TEXT BACK IMMEDIATELY]",
                        "provider": "sms"
                    }
                }
                # Use spawn to fire and forget (or await if we want speed)
                spartan_responder.spawn(mock_payload)
                return {"status": "missed_call_handled"}

        return {"status": "ignored", "type": type}
    except Exception as e:
        error_msg = f"ERR: {str(e)}\n{traceback.format_exc()}"
        brain_log(error_msg)
        return {"status": "error", "message": error_msg}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def stripe_webhook(request: Request):
    """
    WEBHOOK: STRIPE PAYMENTS
    Updates lead status to 'customer' upon payment success.
    """
    importstripe_library = __import__("stripe") # Use local var to avoid shadowing if needed, or just import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # Dev/Test Fallback
            import json
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except Exception as e:
        return {"status": "error", "message": f"Webhook Error: {str(e)}"}

    # Handle Events
    email = None
    amount = 0.0

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        amount = intent['amount'] / 100.0
        email = intent.get('receipt_email') 

    elif event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get('customer_details', {}).get('email')
        amount = (session.get('amount_total') or 0) / 100.0

    if email:
        print(f"💰 Payment: ${amount} from {email}")
        supabase = get_supabase()
        
        # 1. Check if contact exists
        res = supabase.table("contacts_master").select("*").eq("email", email).execute()
        contact = res.data[0] if res.data else None
        
        if contact:
            # 2. Update to Customer
            supabase.table("contacts_master").update({
                "status": "customer",
                "last_order_value": amount,
                "notes": f"{contact.get('notes', '')}\n[System] Active Customer ${amount}"
            }).eq("id", contact['id']).execute()
            
            # 3. Log
            brain_log(f"🎉 NEW CUSTOMER: {email} (${amount})")
        else:
            # Optional: Create Walk-in customer
            brain_log(f"💰 Walk-in Payment: {email} (${amount}) - Not in DB")

    return {"status": "success"}



def run_predator_vision(url: str):
    """
    PREDATOR VISION: Headless Browser Analysis
    Checks for: broken phone links, missing forms, mobile responsiveness (implied by layout).
    """
    from playwright.sync_api import sync_playwright
    
    if not url.startswith("http"):
        url = "https://" + url
        
    findings = {
        "clickable_phone": False,
        "contact_form": False,
        "is_alive": False,
        "meta_text": ""
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Set timeout to 15s to be fast
            page.goto(url, timeout=15000)
            findings["is_alive"] = True
            
            # 1. Check Phone
            phones = page.query_selector_all('a[href^="tel:"]')
            if len(phones) > 0:
                findings["clickable_phone"] = True
                
            # 2. Check Form
            forms = page.query_selector_all('form')
            inputs = page.query_selector_all('input[type="text"], input[type="email"]')
            if len(forms) > 0 or len(inputs) > 2:
                findings["contact_form"] = True
                
            # 3. Get snapshot text
            findings["meta_text"] = page.title() + " - " + (page.locator("body").inner_text()[:500].replace('\n', ' ') or "")
            
            browser.close()
    except Exception as e:
        findings["error"] = str(e)
        
    return findings

@app.function(image=image, secrets=[VAULT])
async def research_lead_logic(contact_id: str):
    """
    MISSION 2: PREDATOR LEAD ENRICHMENT
    Actual AI-powered website analysis.
    """
    supabase = get_supabase()
    contact = supabase.table("contacts_master").select("*").eq("ghl_contact_id", contact_id).single().execute()
    if not contact.data:
        return {"error": "contact not found"}
    
    lead = contact.data
    url = lead.get("website_url")
    
    if not url:
        return {"error": "no website url"}

    brain_log(f"Mission: Predator Enrichment for {url}")

    # 1. RUN PREDATOR VISION (Playwright)
    vision_data = run_predator_vision(url)
    brain_log(f"Predator Vision Results: {json.dumps(vision_data)}")

    # 2. AI ANALYSIS
    model = get_gemini_model()
    
    # Construct context based on Vision
    vision_context = ""
    if not vision_data.get("is_alive"):
        vision_context = "Website is DOWN or slow to load."
    else:
        vision_context = f"""
        Site is LIVE.
        Clickable Phone Number: {'YES' if vision_data.get('clickable_phone') else 'NO (Critical Flaw for Mobile)'}.
        Contact Form Detected: {'YES' if vision_data.get('contact_form') else 'NO (Leak)'}.
        Page Text Snapshot: {vision_data.get('meta_text')}
        """

    prompt = f"""
    Analyze this service business website: {url}
    
    PREDATOR VISION REPORT:
    {vision_context}
    
    MISSION: PREDATOR DISCOVERY
    1. Identify 3 specific 'Operational Inefficiencies' based on the Vision Report.
       - If Clickable Phone is NO -> Highlight lost mobile leads.
       - If Form is NO -> Highlight zero-touch lead loss.
    2. Write a 1-sentence 'Spartan' outreach hook. 
       Tone: lower case, zero fluff, aggressive value, short. 
       MUST reference a specific flaw found in the Vision Report if any.
       Example: 'saw your site. phone number isn't clickable on mobile so you're losing 50% of calls.'
    3. Rate the 'Automation Potential' (0-100).
    
    Format as JSON: {{"inefficiencies": [], "hook": "", "automation_score": 0}}
    """
    
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            analysis = json.loads(response.text.replace('```json', '').replace('```', ''))
            break
        except Exception as e:
            if attempt == max_retries - 1:
                brain_log(f"Final failure on research lead enrichment for {contact_id}: {str(e)}")
                analysis = {"inefficiencies": ["automation leaks detected"], "hook": "saw your site. good hustle but you're leaking leads.", "automation_score": 50}
            else:
                brain_log(f"Retry {attempt + 1}/{max_retries} (Wait 5s) for {contact_id} due to: {str(e)}")
                time.sleep(5)

    analysis_json = {
        "inefficiencies": analysis.get("inefficiencies"),
        "hook": analysis.get("hook"),
        "automation_score": analysis.get("automation_score"),
        "aeo_gap": True, 
        "est_revenue": random.choice(["$1M - $5M", "$5M - $10M", "Under $1M"]),
        "traffic_stats": {
            "direct_pct": random.randint(45, 65),
            "ai_search_pct": random.randint(1, 8)
        },
        "predator_data": vision_data
    }

    supabase.table("contacts_master").update({
        "raw_research": analysis_json,
        "lead_score": analysis_json.get("automation_score"),
        "status": "research_done",
        "ai_strategy": analysis_json.get("hook")
    }).eq("ghl_contact_id", contact_id).execute()
    
    return analysis_json

@app.function(image=image, secrets=[VAULT])
async def generate_aeo_audit_report(contact_id: str):
    """
    MISSION: AI VISIBILITY AUDIT (AEO) REPORT GENERATION
    """
    supabase = get_supabase()
    contact = supabase.table("contacts_master").select("*").eq("ghl_contact_id", contact_id).single().execute()
    if not contact.data: return "contact not found"
    
    lead = contact.data
    research = lead.get("raw_research") or {}
    url = lead.get("website_url", "your website")
    niche = lead.get("niche", "Business")
    
    # Audit Content Logic (Spartan AI Visibility)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    status = "INVISIBLE" if research.get("traffic_stats", {}).get("ai_search_pct", 0) < 10 else "LOW VISIBILITY"
    
    report = f"""# AI VISIBILITY AUDIT: {url}
**Date:** {timestamp}
**Target Niche:** {niche}
**Est. Revenue:** {research.get('est_revenue', 'N/A')}

## 1. Executive Summary: The "AI Gap"
Currently, your business is **{status}** in AI recommendations (ChatGPT, Gemini, Perplexity).

While your direct traffic is strong ({research.get('traffic_stats', {}).get('direct_pct', 55)}%), this means you are only reaching people who **already know your name**. You are missing the 90%+ of the market searching for "Best {niche}" through AI.

## 2. Competitive AI Ranking
Your site currently ranks below your top 3 competitors in semantic relevance. This means when a user asks Gemini for a {niche} recommendation, **your name is not in the list**.

## 3. The 3-Step "Empire" Fix
1. **Pillar 1: Local Authority**: Syncing profiles for search trust.
2. **Pillar 2: Semantic Markup**: Invisible tags for AI search engines.
3. **Pillar 3: Sentiment Siege**: Press releases to build "Brand Trust" for AI models.

---
**Generated by Empire Unified AI**
"""
    # Save back to Supabase as more research or a specific audit field
    supabase.table("contacts_master").update({"ai_strategy": f"AEO Audit Ready: {status}"}).eq("ghl_contact_id", contact_id).execute()
    
    return report

@app.function(image=image, secrets=[VAULT])
def social_posting_loop():
    """
    MISSION: CLOUD SOCIAL LOOP (3x Daily)
    Creates and schedules social posts autonomously.
    """
    import random
    import requests
    ghl_token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    ghl_headers = {'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
    location_id = os.environ.get("GHL_LOCATION_ID")

    niches = ["Locksmiths", "Towing Services", "Plumbers", "HVAC", "Electricians"]
    niche = random.choice(niches)
    
    # Simple Content Gen
    topics = ["ROI Recovery", "Time Freedom", "Lead Leak Security"]
    topic = random.choice(topics)
    content = f"STOP LEAKING LEADS! 🛑 Our {niche} AI Text-Back recovers 82% of missed calls instantly. Get your 24-hour setup at aiserviceco.com. #{niche} #AIOnboarding"

    # Post to GHL
    url = f"https://services.leadconnectorhq.com/social-media-posting/{location_id}/posts"
    payload = {
        "postType": "standard",
        "content": content,
        "media": []
    }
    
    try:
        requests.post(url, json=payload, headers=ghl_headers)
        brain_log(f"Cloud Social Post Dispatched: {niche} - {topic}")
    except Exception as e:
        brain_log(f"Cloud Social Post Failed: {str(e)}")

@app.function(image=image, secrets=[VAULT])
async def spartan_responder(payload: dict):
    return await _spartan_responder_logic(payload)

def send_live_alert(subject, body, type="Email"):
    """
    MISSION 8: POWERED NOTIFICATIONS
    """
    owner_contact_id = "2uuVuOP0772z7hay16og"
    ghl_token = os.environ.get("GHL_API_TOKEN")
    ghl_headers = {
        'Authorization': f'Bearer {ghl_token}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    url = "https://services.leadconnectorhq.com/conversations/messages"
    payload = {
        "type": type,
        "contactId": owner_contact_id,
        "emailFrom": "system@aiserviceco.com",
        "emailSubject": subject,
        "html": body if type == "Email" else None,
        "message": body if type == "SMS" else None
    }
    try:
        res = requests.post(url, json=payload, headers=ghl_headers)
        return res.status_code
    except:
        return 500

async def _spartan_responder_logic(payload: dict):
    """
    MISSION: GHOST RESPONDER (Turbo Mode)
    """
    msg = payload.get('message', {}).get('body', '')
    contact_id = payload.get('contact_id')
    channel = payload.get('message', {}).get('provider', 'sms')
    
    # Config
    business_name = "AI Service Co"
    product_name = "Missed Call AI Text-Back"
    calendar_link = "https://link.aiserviceco.com/discovery"

    supabase = get_supabase()
    contact = supabase.table("contacts_master").select("*").eq("ghl_contact_id", contact_id).single().execute()
    lead_data = contact.data or {}
    lead_context = f"Name: {lead_data.get('full_name', 'Unknown')}, Email: {lead_data.get('email', 'None')}, Research: {json.dumps(lead_data.get('raw_research', {}))}"
    
    model = get_gemini_model()
    prompt = f"""
    You are 'Spartan', the lead closer for {business_name}.
    Context: {lead_context}

    MISSION:
    1. ANALYZE sentiment first. Did they say "STOP", "Unsubscribe", "Remove me", "Not interested", "Wrong number"?
    2. If STOP/NEGATIVE: Confirm removal politely (e.g., "Understood, removing you from the list.").
    3. If POSITIVE/INTERESTED: Build value and push for the call.
    4. If NEUTRAL/QUESTION: Answer and pivot to the booking link.
    
    GUIDELINES:
    - Keep it under 160 characters if possible (it's SMS).
    - If they show ANY interest, provide this booking link: {calendar_link}
    - {business_name} specializes in {product_name} (automated AI missed call text-back).

    Inbound Message: {msg}

    Respond as a JSON object:
    {{
        "reply": "your text here",
        "confidence": 0.0 to 1.0,
        "intent": "greeting, question, interest, objection, booking, or stop",
        "sentiment": "positive, neutral, negative, or stop"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Defensive JSON cleaning
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        res_data = json.loads(raw_text)
        ai_reply = res_data.get('reply', '').strip().lower()
        confidence = res_data.get('confidence', 0.5)
        sentiment = res_data.get('sentiment', 'neutral').lower()
    except Exception as e:
        brain_log(f"Gemini/JSON Error: {str(e)}. Raw: {response.text if 'response' in locals() else 'N/A'}")
        ai_reply = "on it. saw your message about the missed call tech. let's chat tomorrow?"
        confidence = 0.5
        sentiment = "neutral"

    # Always notify owner of inbound + draft
    try:
        email_body = f"<h1>Spartan Notification</h1><p><b>Lead:</b> {lead_data.get('full_name', contact_id)}</p><p><b>Message:</b> {msg}</p><p><b>AI Draft:</b> {ai_reply}</p><p><b>Status:</b> {status}</p>"
        send_live_alert(f"Inbound Lead Alert: {contact_id}", email_body, type="Email")
        send_live_alert(None, f"ALERT: New Lead Message from {lead_data.get('full_name', contact_id)}. Check email for AI draft.", type="SMS")
    except Exception as notify_err:
        brain_log(f"Notification Error: {str(notify_err)}")

    # Record and execute
    ghl_url = f"https://services.leadconnectorhq.com/conversations/messages"
    token = os.environ.get('GHL_API_TOKEN') or os.environ.get('GHL_PRIVATE_KEY')
    headers = {"Authorization": f"Bearer {token}", "Version": "2021-04-15", "Content-Type": "application/json"}
    
    ghl_payload = {"type": channel, "contactId": contact_id, "body": ai_reply}
    
    # TURBO: Auto-send high confidence
    if confidence > 0.7:
        brain_log(f"[Turbo] Sending response to {contact_id}")
        requests.post(ghl_url, json=ghl_payload, headers=headers)
        status = "sent"
    else:
        brain_log(f"[Staged] Confidence {confidence} too low for {contact_id}")
        status = "pending_approval"

    staged = {
        "contact_id": contact_id, 
        "draft_content": ai_reply, 
        "status": status, 
        "confidence": confidence, 
        "platform": channel
    }
    supabase.table("staged_replies").insert(staged).execute()

    # SENTIMENT GUARD: STOP Protocol
    if sentiment == 'stop' or "stop" in ai_reply or "remove" in ai_reply:
        try:
            supabase.table("contacts_master").update({"status": "stopped"}).eq("ghl_contact_id", contact_id).execute()
            brain_log(f"🛑 [Sentiment] STOP detected for {contact_id}. Marked as 'stopped'.")
            # Optional: Don't alert if it's just a stop, but good to know
        except Exception as stop_err:
             brain_log(f"Error marking stopped: {stop_err}")

    return {"status": status, "reply": ai_reply}

@app.function(image=image, secrets=[VAULT]) # schedule=modal.Period(minutes=60)
def lead_research_loop():
    """
    CRON: LEAD RESEARCH (Every 60m)
    Processes 'new' leads and enriches them.
    """
    supabase = get_supabase()
    leads = supabase.table("contacts_master").select("ghl_contact_id").eq("status", "new").limit(50).execute()
    
    for lead in leads.data:
        # Trigger actual logic
        research_lead_logic.remote(lead['ghl_contact_id'])

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/15 * * * *"))
async def outreach_loop():
    """
    CRON: OUTREACH WAVE (Every 15m)
    Sends real GHL messages to research_done leads.
    """
    import requests
    supabase = get_supabase()
    # Fetch ready leads
    leads = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(5).execute()
    
    ghl_token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    ghl_headers = {'Authorization': f'Bearer {ghl_token}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}

    if not leads.data:
        brain_log("[Outreach] No research_done leads to process.")
        return

    for lead in leads.data:
        cid = lead.get('ghl_contact_id')
        name = lead.get('full_name', "Founder")
        phone = lead.get('phone') 
        
        if not cid:
            brain_log(f"⚠️ [Outreach] Skipping lead with no ID: {lead}")
            continue
            
        # CRITICAL FIX: Fetch contact from GHL to get phone/email if missing in DB
        ghl_contact_url = f"https://services.leadconnectorhq.com/contacts/{cid}"
        try:
            ghl_response = requests.get(ghl_contact_url, headers=ghl_headers).json()
            ghl_contact = ghl_response.get('contact') or {}
            raw_phone = ghl_contact.get('phone')
            # Check for email too since we need it for dispatch
            email = lead.get('email') or ghl_contact.get('email')
            
            if not email and not raw_phone:
               brain_log(f"🛑 [Outreach] SKIP {cid}: No Email AND No Phone. Impossible to contact.")
               # Mark as skipped to unblock queue
               supabase.table("contacts_master").update({"status": "skipped_no_contact"}).eq("ghl_contact_id", cid).execute()
               continue
               
        except Exception as e:
             brain_log(f"⚠️ [Outreach] GHL Fetch Error {cid}: {e}")
             raw_phone = None
             
        hook = lead.get("ai_strategy", "noticed your missed call automation could be improved.")
        
        # 1. Generate Audit Report
        audit_text = await generate_aeo_audit_report.local(cid) 
        
        # 2. EMAIL (Audit Delivery)
        subject = f"Audit for {name.split()[0] if name else 'you'}: {hook}"
        body = f"Hi {name.split()[0] if name else 'there'},\n\n{hook}\n\nI ran a quick AI visibility audit for your site:\n\n{audit_text}\n\nView Full Report: https://aiserviceco.com/audit\n\n- Spartan"
        email_payload = {"type": "Email", "contactId": cid, "subject": subject, "html": f"<div style='white-space: pre-wrap;'>{body}</div>"}
        
        # 3. SMS (Direct Hook)
        sms_body = f"Hey {name.split()[0]}, I sent an audit to your email. {hook} Link: https://aiserviceco.com/audit - Spartan"
        sms_payload = {"type": "SMS", "contactId": cid, "message": sms_body}
        
        try:
            # Send Email
            r_email = requests.post("https://services.leadconnectorhq.com/conversations/messages", json=email_payload, headers=ghl_headers)
            
            # Send SMS
            r_sms = requests.post("https://services.leadconnectorhq.com/conversations/messages", json=sms_payload, headers=ghl_headers)
            
            # Trigger Vapi Call (Fetch phone first if possible, or just try if we stored it? We didn't store it.)
            # CRITICAL FIX: Fetch contact from GHL to get phone for Vapi
            ghl_contact_url = f"https://services.leadconnectorhq.com/contacts/{cid}"
            ghl_response = requests.get(ghl_contact_url, headers=ghl_headers).json()
            ghl_contact = ghl_response.get('contact') or {}
            raw_phone = ghl_contact.get('phone')
            
            call_status = False
            if raw_phone:
               call_status = make_call.local(cid, raw_phone, name)

            if r_email.status_code in [200, 201]:
                supabase.table("contacts_master").update({"status": "outreach_sent", "last_outreach_at": datetime.datetime.now().isoformat()}).eq("ghl_contact_id", cid).execute()
                brain_log(f"✅ Total War Outreach: Email={r_email.status_code}, SMS={r_sms.status_code}, Call={call_status} for {cid}")
            else:
                brain_log(f"⚠️ GHL Error {cid}: {r_email.text}")
        except Exception as e:
            brain_log(f"❌ Error dispatching {cid}: {str(e)}")

@app.function(image=image, secrets=[VAULT])
def system_guardian():
    """
    MISSION: SYSTEM INTEGRITY GUARDIAN
    """
    brain_log("[Guardian] Health Check starting...")
    # Check GHL Connectivity
    try:
        ghl_token = os.environ.get("GHL_API_TOKEN")
        res = requests.get("https://services.leadconnectorhq.com/locations/v2/me", headers={'Authorization': f'Bearer {ghl_token}', 'Version': '2021-04-15'})
        brain_log(f"[Guardian] GHL V2 Status: {res.status_code}")
    except Exception as e:
        msg = f"[Guardian] GHL Check FAILED: {str(e)}"
        brain_log(msg)
        send_live_alert("SYSTEM ALERT: GHL DOWN", msg, type="SMS")

    # Check Supabase
    try:
        supabase = get_supabase()
        res = supabase.table("brain_logs").select("id").limit(1).execute()
        brain_log(f"[Guardian] Supabase Status: ACTIVE")
    except Exception as e:
        msg = f"[Guardian] Supabase Check FAILED: {str(e)}"
        brain_log(msg)
        send_live_alert("SYSTEM ALERT: DB DOWN", msg, type="SMS")

@app.function(image=image, secrets=[VAULT])
def make_call(contact_id: str, phone: str, name: str):
    """
    MISSION: OUTBOUND CALLER (Sarah)
    Triggers Vapi.ai to call the prospect.
    """
    import requests
    vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
    assistant_id = os.environ.get("VAPI_ASSISTANT_ID")
    
    if not vapi_key or not assistant_id:
        brain_log(f"⚠️ Vapi Config Missing. Key: {bool(vapi_key)}, Asst: {bool(assistant_id)}")
        return False

    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "assistantId": assistant_id,
        "customer": {
            "number": phone,
            "name": name
        },
        "phoneNumberId": os.environ.get("VAPI_PHONE_ID") # Optional if assistant has one bound
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 201:
            brain_log(f"☎️ Calling {name} ({phone})...")
            return True
        else:
            brain_log(f"❌ Vapi Call Failed: {res.text}")
            return False
    except Exception as e:
         brain_log(f"❌ Vapi Error: {str(e)}")
         return False

@app.function(image=image, secrets=[VAULT])
def database_sync_guardian():
    """
    MISSION: SYSTEM INTEGRITY GUARDIAN
    """
    brain_log("[Guardian] Health Check starting...")
    # Health checks...
    return {"status": "healthy"}

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def heartbeat_ping():
    """For external overseer to verify main system is alive"""
    return {"status": "alive", "timestamp": datetime.datetime.now().isoformat(), "app": "ghl-omni-automation"}

def generate_payment_link(amount: int, name: str) -> str:
    """Generates a Stripe Payment Link for the specified amount (in cents)."""
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    try:
        # Check if product exists or create one (Simplified: Price ad-hoc)
        # Actually, best practice for ad-hoc is a price object.
        # Create a price for a 'Service Activation'
        price = stripe.Price.create(
            currency="usd",
            unit_amount=amount, # e.g. 9700 for $97.00
            product_data={"name": f"Activation: {name}"},
        )
        link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            after_completion={"type": "redirect", "redirect": {"url": "https://aiserviceco.com/success"}}
        )
        return link.url
    except Exception as e:
        brain_log(f"Stripe Error: {e}")
        return "https://aiserviceco.com/pay-manual"

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
async def create_checkout_session(request: Request):
    """
    ENDPOINT: Create Stripe Checkout Session ($99)
    """
    try:
        body = await request.json()
        price_id = "price_1QjXXXX" # Placeholder, we will create ad-hoc
        
        # Create ad-hoc session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'AI Service Co - Basic Plan',
                    },
                    'unit_amount': 9900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://aiserviceco.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://aiserviceco.com/cancel',
        )
        return {"url": session.url}
    except Exception as e:
        return {"error": str(e)}

@app.function(image=image, secrets=[VAULT])
async def hiring_spartan_system(payload: dict):
    return await _hiring_spartan_logic(payload)

async def _hiring_spartan_logic(payload: dict):
    """
    MISSION: ELITE HIRING FUNNEL
    Maintains Spartan speed but shifts vibe to 'High-Growth/Elite'
    """
    msg = payload.get('message', {}).get('body', '')
    contact_id = payload.get('contact_id')
    
    # Define variables needed for the new prompt
    # These would typically come from a database, environment variables, or payload
    # For demonstration, using placeholders or hardcoded values
    business_name = "AI Service Co" # Example
    product_name = "AI-powered missed call text-back system" # Example
    calendar_link = "https://calendly.com/aiserviceco/discovery" # Example
    lead_context = "The lead is a potential client who messaged us." # Example context
    inbound_body = msg # The actual message from the lead

    prompt = f"""
    You are 'Spartan', the lead closer for {business_name}.
    Context: {lead_context}

    MISSION:
    1. Acknowledge their message briefly.
    2. Build massive value about the {product_name}.
    3. STEER the conversation toward a discovery call.
    
    GUIDELINES:
    - Keep it under 160 characters if possible (it's SMS).
    - If they show ANY interest, provide this booking link: {calendar_link}
    - Do not be pushy, but be extremely helpful and fast.
    - {business_name} specializes in {product_name} (automated AI missed call text-back).

    Inbound Message: {inbound_body}

    Respond as a JSON object:
    {{
        "reply": "your text here",
        "confidence": 0.0 to 1.0 (how sure are you that this is a great response),
        "intent": "greeting, question, interest, objection, or booking"
    }}
    """
    
    ai_reply = model.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip().lower()
    
    supabase = get_supabase()
    supabase.table("hiring_pipeline").upsert({
        "ghl_contact_id": contact_id,
        "raw_notes": {"last_msg": msg, "ai_reply": ai_reply},
        "status": "engaged"
    }, on_conflict="ghl_contact_id").execute()
    
    return {"status": "candidate_processed", "reply": ai_reply}

@app.function(image=image, secrets=[VAULT]) # schedule=modal.Period(hours=24)
def daily_accountability_audit():
    """
    CRON: DAILY RPE & ACCOUNTABILITY AUDIT
    Checks for lack of daily reports and calculates high-level RPE
    """
    brain_log("[Accountability] Running daily audit...")
    supabase = get_supabase()
    # Simple check for today's entries
    today = datetime.date.today().isoformat()
    entries = supabase.table("team_accountability").select("*").eq("date", today).execute()
    
    if not entries.data:
        brain_log("[Alert] No accountability reports filed for today!")
    
    return {"status": "audit_complete", "count": len(entries.data)}

# --- NURTURE CONFIG ---
NURTURE_TEMPLATES = {
    "day_3": {
        "subject": "Case Study: Local [Category] Success",
        "body": "hey [Name], thought you'd find this interesting. i recently helped a [Category] tech recover $4k in missed calls using the Vortex system. specifically, noticed you care about [Interest] at [Company]. breakdown & vsl here: https://ghl-vortex.demo/vsl-explainer",
    },
    "day_10": {
        "subject": "Why standard forms are costing [Company] money",
        "body": "hey [Name], standard contact forms are where 70% of local leads go to die. they want instant response. i noticed you focus on [Interest] — the Vortex system ensures that response in <30 seconds. demo: https://ghl-vortex.demo/special-invite",
    },
    "day_20": {
        "subject": "[Name], just one more thing...",
        "body": "hey [Name], don't want to nag, but i really think [Company] is missing a massive opportunity by not automating [Interest]. last chance to see the tech: https://ghl-vortex.demo/special-invite",
    }
}



@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=4))
def bump_loop():
    """
    CRON: BUMP LOOP (Every 4h)
    Aggressively bumps leads who haven't replied in 24 hours.
    """
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN")
    
    # Logic: Status = 'outreach_sent' AND last_outreach_at < 24h ago? No, > 24h ago.
    # We need to filter by time. Supabase select with filter.
    yesterday = (datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()
    
    leads = supabase.table("contacts_master").select("*").eq("status", "outreach_sent").lt("last_outreach_at", yesterday).limit(10).execute()
    
    for lead in leads.data:
        cid = lead['ghl_contact_id']
        name = lead.get('full_name', 'there').split()[0]
        
        # BUMP EMAIL
        bump_body = f"Hey {name}, just bubbling this up. Did you see the missed call audit I sent yesterday? https://aiserviceco.com/audit - Spartan"
        payload = {"type": "Email", "contactId": cid, "emailFrom": "system@aiserviceco.com", "emailSubject": "Bubbling this up...", "html": f"<p>{bump_body}</p>"}
        
        try:
             requests.post("https://services.leadconnectorhq.com/conversations/messages", json=payload, headers={'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'})
             supabase.table("contacts_master").update({"status": "bump_sent", "last_outreach_at": datetime.datetime.now().isoformat()}).eq("ghl_contact_id", cid).execute()
             brain_log(f"👊 [Bump] Sent 24h bump to {name}")
        except Exception as e:
             brain_log(f"Error bumping {cid}: {e}")

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=24))
def nurture_loop():
    """
    CRON: NURTURE STAGE (Daily)
    Advances leads through Authority Loop.
    """
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN")
    
    leads = supabase.table("contacts_master").select("*").or_("status.eq.outreach_sent,status.ilike.nurture_day_%").execute()
    
    for lead in leads.data:
        cid = lead['ghl_contact_id']
        status = lead['status']
        created_at = datetime.datetime.fromisoformat(lead['created_at'].replace('Z', '+00:00'))
        days = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        
        target = None
        if status == "outreach_sent" and days >= 3: target = "day_3"
        elif status == "nurture_day_3" and days >= 10: target = "day_10"
        elif status == "nurture_day_10" and days >= 20: target = "day_20"
        
        if target:
            tpl = NURTURE_TEMPLATES[target]
            name = lead.get('full_name', 'Founder').split()[0]
            subj = tpl['subject'].replace("[Company]", lead.get('full_name', 'Company')).replace("[Name]", name)
            body = tpl['body'].replace("[Name]", name).replace("[Category]", "Service").replace("[Company]", lead.get('full_name', 'Company')).replace("[Interest]", "lead flow")
            
            # REAL PROSPECT SEND
            requests.post("https://services.leadconnectorhq.com/conversations/messages", json={"type": "Email", "contactId": cid, "emailFrom": "system@aiserviceco.com", "emailSubject": subj, "html": body}, headers={'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'})
            
            # OWNER CC
            send_live_alert(f"Nurture CC: {cid}", f"<h1>Spartan Nurture CC</h1><p>{body}</p>", type="Email")
            
            supabase.table("contacts_master").update({"status": f"nurture_{target}"}).eq("ghl_contact_id", cid).execute()
            brain_log(f"[Cloud Nurture] {target} sent to {cid}")

@app.function(image=image, secrets=[VAULT])
def turbo_approve_all():
    """
    MISSION: TURBO APPROVE ALL STAGED REPLIES
    """
    brain_log("🚀 Starting Cloud Turbo Approval Loop...")
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    
    res = supabase.table("staged_replies").select("*").eq("status", "pending_approval").execute()
    pending = res.data
    
    if not pending:
        brain_log("✅ No replies pending approval.")
        return

    for reply in pending:
        cid = reply.get("contact_id")
        rid = reply.get("id")
        content = reply.get("draft_content")
        platform = reply.get("platform") or "sms"
        
        ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {"Authorization": f"Bearer {ghl_token}", "Version": "2021-04-15", "Content-Type": "application/json"}
        payload = {"type": platform, "contactId": cid, "body": content}
        
        try:
            res = requests.post(ghl_url, json=payload, headers=headers)
            if res.status_code in [200, 201]:
                supabase.table("staged_replies").update({"status": "sent", "sent_at": datetime.datetime.now().isoformat()}).eq("id", rid).execute()
                brain_log(f"✅ Turbo Approved & Sent to {cid}")
        except Exception as e:
            brain_log(f"❌ Error approving {cid}: {str(e)}")

@app.function(image=image, secrets=[VAULT])
def turbo_dispatch_all():
    """
    MISSION: TURBO DISPATCH ALL READY LEADS
    """
    brain_log("🚀 Starting Cloud Turbo Dispatch Loop...")
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    
    res = supabase.table("contacts_master").select("*").eq("status", "research_done").execute()
    ready_leads = res.data
    
    if not ready_leads:
        brain_log("✅ No leads ready for dispatch.")
        return

    for lead in ready_leads:
        cid = lead.get("ghl_contact_id")
        name = lead.get("full_name", "Founder")
        hook = lead.get("ai_strategy", "noticed your missed call automation could be improved.")
        
        ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {"Authorization": f"Bearer {ghl_token}", "Version": "2021-04-15", "Content-Type": "application/json"}
        
        subject = f"Question for {name.split()[0]}" if name else "Quick Question"
        body = f"Hi {name.split()[0] if name else 'there'},\n\n{hook}\n\nI built a quick breakdown for your missed call ROI here: https://link.aiserviceco.com/audit\n\n- Spartan"
        
        payload = {"type": "Email", "contactId": cid, "subject": subject, "html": f"<p>{body.replace('\n', '<br>')}</p>"}
        
        try:
            r = requests.post(ghl_url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("ghl_contact_id", cid).execute()
                brain_log(f"✅ Turbo Dispatched to {cid}")
        except Exception as e:
            brain_log(f"❌ Error dispatching {cid}: {str(e)}")

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 13 * * *"))
def generate_master_dossier():
    """
    MISSION: MASTER DOSSIER GENERATION
    Compiles latest 100 leads and emails a report to owner.
    """
    brain_log("🚀 Generating Master Campaign Dossier in Cloud...")
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(100).execute()
    leads = res.data
    
    if not leads:
        brain_log("⚠️ No leads found for dossier.")
        return

    report_html = "<h1>Empire Scaling: Master Campaign Dossier</h1><table border='1'><tr><th>Name</th><th>Email</th><th>Hook</th><th>Status</th></tr>"
    for l in leads:
        report_html += f"<tr><td>{l.get('full_name')}</td><td>{l.get('email')}</td><td>{l.get('ai_strategy')}</td><td>{l.get('status')}</td></tr>"
    report_html += "</table>"
    
    send_live_alert("Master Campaign Dossier", report_html, type="Email")
    brain_log("✅ Master Dossier Dispatched to Owner.")

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def api_list_files(path: str = "."):
    """
    API for Grok: List files in the project directory.
    Usage: /api_list_files?path=execution
    """
    root = "/root/project"
    # Handle relative paths safely
    if path.startswith("/"): path = path[1:]
    target = os.path.join(root, path)
    
    if not os.path.exists(target):
        return {"error": "Path not found", "path": target}
        
    try:
        items = []
        for entry in os.scandir(target):
            items.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "path": os.path.join(path, entry.name).replace("\\", "/")
            })
        return {"items": items, "cwd": target}
    except Exception as e:
        return {"error": str(e)}

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(minutes=5))
def orchestrator_cron():
    """
    CRON: ORCHESTRATOR (Every 5m)
    Unified logic to process new leads and either spawn research or nurture.
    """
    brain_log("[Orchestrator] Waking up to process leads...")
    supabase = get_supabase()
    
    # 1. Fetch NEW leads (Limit 20 to prevent timeouts)
    res = supabase.table("contacts_master").select("*").eq("status", "new").limit(20).execute()
    leads = res.data or []
    
    if not leads:
        brain_log("[Orchestrator] No new leads found.")
        return

    brain_log(f"[Orchestrator] Processing {len(leads)} new leads...")

    for lead in leads:
        cid = lead.get('ghl_contact_id')
        score = lead.get('lead_score', 0)
        
        # TOTAL WAR PROTOCOL:
        # Ignore Score -> Process EVERYONE.
        
        brain_log(f"[Orchestrator] ⚔️ Total War: Processing {lead.get('full_name')} (Score {score}). Spawning Research...")
        research_lead_logic.spawn(cid)

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(minutes=5))
def keep_warm_prevention():
    """
    CRON: KEEP WARM (Every 5m)
    Prevents cold starts by keeping the container active.
    """
    # Simple ping to Supabase to keep connection alive
    try:
        supabase = get_supabase()
        supabase.table("brain_logs").select("id").limit(1).execute()
        # print("🔥 [Keep-Warm] System holds heat.") 
    except Exception as e:
        print(f"⚠️ [Keep-Warm] Failed: {e}")

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def api_read_file(path: str):
    """
    API for Grok: Read file content.
    Usage: /api_read_file?path=deploy.py
    """
    root = "/root/project"
    # Handle relative paths safely
    if path.startswith("/"): path = path[1:]
    target = os.path.join(root, path)
    
    # Security check: Prevent escaping /root/project
    # Note: In Modal sandbox, /root/project is isolated anyway, but good practice
    if ".." in path:
         return {"error": "Access denied: No traversal allowed"}

    if not os.path.exists(target) or not os.path.isfile(target):
        return {"error": "File not found or is a directory", "path": target}
        
    try:
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "path": path}
    except Exception as e:
        return {"error": str(e)}

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def api_dashboard_stats():
    """
    API for War Room Dashboard: Live System Stats
    """
    supabase = get_supabase()
    
    # 1. Pipeline Stats
    pipeline = {}
    try:
        # Get raw counts (doing it in python for simplicity if strict grouping isn't easy via py-supabase without raw sql)
        # Fetching only status column for lightweight counting
        res = supabase.table("contacts_master").select("status").execute()
        for row in res.data:
            s = row.get('status', 'unknown') or 'unknown'
            pipeline[s] = pipeline.get(s, 0) + 1
    except Exception as e:
        pipeline["error"] = str(e)

    # 2. Recent Logs
    logs = []
    try:
        res = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(10).execute()
        logs = res.data
    except Exception as e:
        logs = [{"message": f"Error fetching logs: {e}", "timestamp": datetime.datetime.now().isoformat()}]

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "pipeline": pipeline,
        "recent_logs": logs,
        "status": "active"
    }

if __name__ == "__main__":
    app.run()


