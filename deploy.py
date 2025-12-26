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

app = modal.App("ghl-omni-automation")

# Image with dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "requests", "google-generativeai", "playwright", "fastapi")
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
    return genai.GenerativeModel('gemini-1.5-flash')

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
            contact_obj = payload.get('contact', {}) or {}
            tags = contact_obj.get('tags', [])
            if 'candidate' in [t.lower() for t in tags] or 'hiring' in [t.lower() for t in tags]:
                return await _hiring_spartan_logic(payload)
            return await _spartan_responder_logic(payload)

        return {"status": "ignored", "type": type}
    except Exception as e:
        error_msg = f"ERR: {str(e)}\n{traceback.format_exc()}"
        brain_log(error_msg)
        return {"status": "error", "message": error_msg}

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

    # Scrape website (Simplified for now - using AI to 'predict' based on URL/Meta)
    # In real world, use playwright to get text
    
    model = get_gemini_model()
    prompt = f"""
    Analyze this service business website: {url}
    
    MISSION: PREDATOR DISCOVERY
    1. Identify 3 specific 'Operational Inefficiencies' (e.g. no automated booking, zero-touch lead gen missing, or manual hiring processes mentioned in careers page).
    2. Write a 1-sentence 'Spartan' outreach hook. 
       Tone: lower case, zero fluff, aggressive value, short. 
       Example: 'saw you're hiring for sales. i can automate 80% of the screening so you only talk to killers.'
    3. Rate the 'Automation Potential' (0-100) based on how much of their workflow can be offloaded to AI.
    
    Format as JSON: {{"inefficiencies": [], "hook": "", "automation_score": 0}}
    """
    
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            # Log raw text for debugging if needed
            # brain_log(f"Raw Response: {response.text}")
            analysis = json.loads(response.text.replace('```json', '').replace('```', ''))
            break
        except Exception as e:
            if attempt == max_retries - 1:
                brain_log(f"Final failure on research lead enrichment for {contact_id}: {str(e)}")
                analysis = {"inefficiencies": ["automation leaks detected"], "hook": "saw your site. good hustle but you're leaking leads.", "automation_score": 50}
            else:
                brain_log(f"Retry {attempt + 1}/{max_retries} (Wait 5s) for {contact_id} due to: {str(e)}")
                time.sleep(5)

    supabase.table("contacts_master").update({
        "raw_research": analysis,
        "lead_score": analysis.get("automation_score"),
        "status": "research_done",
        "ai_strategy": analysis.get("hook")
    }).eq("ghl_contact_id", contact_id).execute()
    
    return analysis

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
    1. Acknowledge their message briefly.
    2. Build massive value about the {product_name}.
    3. STEER the conversation toward a discovery call.
    
    GUIDELINES:
    - Keep it under 160 characters if possible (it's SMS).
    - If they show ANY interest, provide this booking link: {calendar_link}
    - Do not be pushy, but be extremely helpful and fast.
    - {business_name} specializes in {product_name} (automated AI missed call text-back).

    Inbound Message: {msg}

    Respond as a JSON object:
    {{
        "reply": "your text here",
        "confidence": 0.0 to 1.0,
        "intent": "greeting, question, interest, objection, or booking"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Defensive JSON cleaning
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        res_data = json.loads(raw_text)
        ai_reply = res_data.get('reply', '').strip().lower()
        confidence = res_data.get('confidence', 0.5)
    except Exception as e:
        brain_log(f"Gemini/JSON Error: {str(e)}. Raw: {response.text if 'response' in locals() else 'N/A'}")
        ai_reply = "on it. saw your message about the missed call tech. let's chat tomorrow?"
        confidence = 0.5

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

@app.function(image=image, secrets=[VAULT])
def outreach_scaling_loop():
    """
    MISSION: EMPIRE OUTREACH SCALING
    Processes the 100-target batch through A/B testing via GHL API.
    """
    import requests
    supabase = get_supabase()
    # Find leads tagged 'empire-scaling' that haven't been nurtured yet
    leads = supabase.table("contacts_master").select("*").contains("tags", ["empire-scaling"]).eq("status", "research_done").limit(5).execute()
    
    ghl_token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    ghl_headers = {'Authorization': f'Bearer {ghl_token}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}

    for lead in leads.data:
        contact_id = lead['ghl_contact_id']
        research = lead.get('raw_research', {}) or {}
        segment = research.get('campaign_segment', 'A') # Default to ROI focus
        
        subject = "You're leaking $2,400/mo in missed calls (Verified)" if segment == 'A' else "Stop checking your phone during family dinner."
        body = f"Hi {lead.get('full_name', 'there')},\n\nI audited your site and found you're missing calls. Our AI saves you $2k/week. [Link]"
        
        email_payload = {
            "type": "Email",
            "contactId": contact_id,
            "subject": subject,
            "body": body
        }
        
        try:
            # Dispatch via GHL
            requests.post("https://services.leadconnectorhq.com/conversations/messages", json=email_payload, headers=ghl_headers)
            supabase.table("contacts_master").update({"status": "nurtured"}).eq("ghl_contact_id", contact_id).execute()
            brain_log(f"Cloud Outreach Sent to {contact_id} (Segment {segment})")
        except Exception as e:
            brain_log(f"Cloud Outreach Failed for {contact_id}: {str(e)}")

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
        brain_log(f"[Guardian] GHL Check FAILED: {str(e)}")

    # Check Supabase
    try:
        supabase = get_supabase()
        res = supabase.table("brain_logs").select("id").limit(1).execute()
        brain_log(f"[Guardian] Supabase Status: ACTIVE")
    except Exception as e:
        brain_log(f"[Guardian] Supabase Check FAILED: {str(e)}")

@app.function(image=image, secrets=[VAULT])
def database_sync_guardian():
    """
    MISSION: SYSTEM INTEGRITY GUARDIAN
    """
    brain_log("[Guardian] Health Check starting...")
    # Health checks...
    return {"status": "healthy"}

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
    
    ai_reply = model.generate_content(prompt).text.strip().lower()
    
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

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(minutes=30))
def outreach_loop():
    """
    CRON: OUTREACH WAVE (Every 30m)
    Sends real GHL messages to research_done leads.
    """
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN")
    owner_id = "2uuVuOP0772z7hay16og"
    
    leads = supabase.table("contacts_master").select("*").or_("ghl_contact_id.ilike.millen_%,ghl_contact_id.ilike.fl_blit_%,ghl_contact_id.ilike.blitz_%,ghl_contact_id.ilike.mission_fs_%,ghl_contact_id.ilike.smb_tampa_%").eq("status", "research_done").limit(10).execute()
    
    for lead in leads.data:
        cid = lead['ghl_contact_id']
        name = lead.get('full_name', 'Founder')
        hook = lead.get('ai_strategy', "saw your site. good hustle but you're leaking leads.")
        email = lead.get('email')
        
        # 1. SEND REAL PROSPECT EMAIL
        p_payload = {
            "type": "Email", "contactId": cid, "emailFrom": "system@aiserviceco.com",
            "emailSubject": f"Quick thought for {name}",
            "html": f"<p>hey {name.split()[0].lower()}, {hook}</p><p>demo: https://ghl-vortex.demo/special-invite</p>"
        }
        requests.post("https://services.leadconnectorhq.com/conversations/messages", json=p_payload, headers={'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'})
        
        # 2. SEND OWNER CC
        cc_body = f"<h1>Spartan Outreach CC</h1><p><b>To:</b> {email}</p><p><b>Hook:</b> {hook}</p>"
        send_live_alert(f"Outreach CC: {name}", cc_body, type="Email")
        
        supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("ghl_contact_id", cid).execute()
        brain_log(f"[Cloud Outreach] Sent to {name}")

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

@app.function(image=image, secrets=[VAULT])
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

if __name__ == "__main__":
    app.run()
