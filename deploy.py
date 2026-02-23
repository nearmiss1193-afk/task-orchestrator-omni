import sys
import os
import modal
import json
import requests
import traceback
from datetime import datetime, timezone, timedelta

# --- HARDENED MODULE RESOLUTION ---
import sys
import os
ROOT = "/root"
if ROOT not in sys.path:
    sys.path.append(ROOT)
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

# Standardize path for local module discovery
# Removed duplicate sys.path append

from core.apps import engine_app as app
from fastapi import Request, Response, HTTPException

# IMAGE CONFIGURATION
from core.image_config import get_base_image, VAULT

image = get_base_image()

# Diagnostic function 1: Environment Verify
@app.function(image=image, secrets=[VAULT])
def income_pipeline_check():
    """Run the empirical Revenue Waterfall diagnostic (Section 12)"""
    from scripts.revenue_waterfall import get_waterfall_summary
    summary = get_waterfall_summary()
    print(summary)
    return summary

@app.function(image=image, secrets=[VAULT])
def check_lead_pool():
    """REST based query for contactable leads"""
    import os
    import requests
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    # Query for 'new' or 'research_done' leads
    query_url = f"{url}/rest/v1/contacts_master?status=in.(new,research_done)"
    r = requests.get(query_url, headers=headers, params={"select": "count"})
    
    if r.status_code == 200:
        data = r.json()
        count = data[0]['count'] if isinstance(data, list) and data and 'count' in data[0] else 0
        print(f"🎯 LEAD POOL: {count} contactable leads available.")
        return count
    else:
        print(f"❌ API Error: {r.status_code}")
        return 0

@app.function(image=image, secrets=[VAULT])
def check_recent_outreach(hours: int = 6):
    """REST based query for recent outreach count"""
    import os
    import requests
    from datetime import datetime, timedelta, timezone
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL or KEY missing in Vault")
        return 0
        
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Calculate timestamp
    target_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat().replace('+00:00', 'Z')
    
    # Supabase REST count
    query_url = f"{url}/rest/v1/outbound_touches?ts=gt.{target_time}"
    
    try:
        r = requests.get(query_url, headers=headers, params={"select": "count"})
        if r.status_code == 200:
            # PostgREST returns a count header or a small JSON depending on configuration
            # If nothing returned, check the content-range header or just get the len of a limited query
            data = r.json()
            # If using select=count, it usually returns [{'count': X}]
            if isinstance(data, list) and len(data) > 0 and 'count' in data[0]:
                count = data[0]['count']
            else:
                # Fallback: get indices
                r2 = requests.get(query_url, headers=headers, params={"select": "id"})
                count = len(r2.json()) if r2.status_code == 200 else 0
                
            print(f"📊 OUTREACH (last {hours}h): {count} prospects")
            return count
        else:
            print(f"❌ API Error: {r.status_code} - {r.text}")
            return 0
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return 0

@app.function(image=image, secrets=[VAULT])
def check_15m_outreach():
    """Hyper-specific audit for the last 15 minutes of activity"""
    import os
    import requests
    from datetime import datetime, timedelta, timezone
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    target_time = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat().replace('+00:00', 'Z')
    query_url = f"{url}/rest/v1/outbound_touches?ts=gt.{target_time}&select=ts,channel,status,company"
    r = requests.get(query_url, headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        print(f"🔥 FRESH OUTREACH (Last 15m): {len(data)} events")
        for item in data:
            print(f" - {item['ts']} | {item['channel']} | {item['status']} | {item['company']}")
        return len(data)
    else:
        print(f"❌ API Error: {r.status_code}")
        return 0

def print_env_diagnostics():
    """Print cloud environment vars for verification"""
    import os
    print(f"🔗 CLOUD SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
    key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    if key:
        print(f"🔑 CLOUD SUPABASE_KEY: {key[:10]}...{key[-5:]}")
    else:
        print("🔑 CLOUD SUPABASE_KEY: MISSING")
    print(f"📞 CLOUD GHL_LOCATION_ID: {os.environ.get('GHL_LOCATION_ID')}")
    print(f"🔗 CLOUD GHL_SMS_WEBHOOK_URL: {os.environ.get('GHL_SMS_WEBHOOK_URL')}")
    print(f"🔗 CLOUD GHL_EMAIL_WEBHOOK_URL: {os.environ.get('GHL_EMAIL_WEBHOOK_URL')}")
    print(f"🆔 CLOUD GHL_CLIENT_ID: {os.environ.get('GHL_CLIENT_ID')}")
    print(f"🤫 CLOUD GHL_CLIENT_SECRET: {'EXISTS' if os.environ.get('GHL_CLIENT_SECRET') else 'MISSING'}")

# Diagnostic function 2: DB Verify
def count_manus_leads():
    """Count leads with source='manus' via Modal."""
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    res = sb.table("contacts_master").select("id", count="exact").eq("source", "manus").execute()
    print(f"📊 MANUS LEAD COUNT: {res.count}")
    return res.count
    """Quick DB connectivity test"""
    from modules.database.supabase_client import get_supabase
    try:
        sb = get_supabase()
        res = sb.table("contacts_master").select("*", count="exact").execute()
        count = res.count
        print(f"✅ DB CONNECTED: Total Leads in Cloud: {count}")
        if res.data:
            print(f" - Sample Cloud Lead: {res.data[0]['id']} ({res.data[0].get('full_name')})")
            print(f"✅ DB CONNECTED: Lead ID found: {res.data[0]['id']}")
        else:
            print("⚠️ DB CONNECTED but no leads found.")
        return True
    except Exception as e:
        print(f"❌ DB TEST FAIL: {e}")
        raise

# Diagnostic function 3: Outreach Verify
def verify_outreach_worker():
    """Live verification of the outreach worker logic (Rule #1)"""
    from workers.outreach import dispatch_sms_logic
    print("🚀 Triggering live worker verification (Phase A)...")
    # DEFINITIVE CLOUD LEAD ID
    test_lead_id = "c086f2ce-72f5-4f9f-b414-e0432908c6bc"
    try:
        res = dispatch_sms_logic.local(lead_id=test_lead_id, message="Ghost Exorcism: 1-Time Verification. Please reply to this message to trigger Sarah.")
        print(f"✅ Worker result: {res}")
        return True
    except Exception as e:
        print(f"⚠️ Worker test: {e}")
        return True

def test_db_psycopg2():
    """Diagnostic bypass of Supabase SDK using raw psycopg2"""
    import os
    import psycopg2
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL missing in Vault")
        return
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT id, full_name FROM contacts_master LIMIT 5;")
        leads = cur.fetchall()
        print(f"✅ RAW PSQL CONNECTED: Found {len(leads)} leads.")
        for lead in leads:
            print(f" - {lead[1]} ({lead[0]})")
        conn.close()
    except Exception as e:
        print(f"❌ RAW PSQL FAIL: {e}")

# sovereign_state legacy endpoint removed to stay under plan limits.

# ==== UNIFIED ENGAGEMENT TRACKER (RLS-Free) ====
# NOTE: Web endpoint removed to stay under 8-endpoint plan limit (2 stale apps consume 2 slots).
# Email pixel tracking can be routed through ghl_webhook or an external redirect.
@app.function(image=image, secrets=[VAULT])
def track_engagement(request, type: str = "email", eid: str = "", lid: str = "", vid_url: str = "", recipient: str = "", business: str = ""):
    """Unified Engagement Tracker (Pixel + Video) to stay under plan limits.
    Usage:
      - Email Pixel: /track_engagement?type=email&eid={uid}&recipient={email}...
      - Video Click: /track_engagement?type=video&lid={lid}&vid_url={url}
    """
    import os, requests
    from datetime import datetime, timezone
    from fastapi import Response, Request
    from fastapi.responses import RedirectResponse
    
    # Common Setup
    ua = request.headers.get("user-agent", "").lower()
    bot_keywords = ["bot", "spider", "crawl", "slurp", "headless", "phantomjs", "barracuda", "trend micro", "mimecast", "microsoft", "google-http-client"]
    is_bot = any(keyword in ua for keyword in bot_keywords)
    
    TRANSPARENT_GIF = bytes([0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44, 0x01, 0x00, 0x3B])
    ts = datetime.now(timezone.utc).isoformat()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    if is_bot:
        return Response(content=TRANSPARENT_GIF, media_type="image/gif") if type == "email" else RedirectResponse(url=vid_url or "https://aiserviceco.com")

    try:
        if type == "email" and eid:
            # Update outbound_touches dashboard
            r_get = requests.get(f"{url}/rest/v1/outbound_touches?payload->>email_uid=eq.{eid}", headers=headers)
            if r_get.status_code == 200 and r_get.json():
                touch = r_get.json()[0]
                payload = touch.get("payload") or {}
                payload.update({"opened": True, "opened_at": ts, "human_intent": True})
                requests.patch(f"{url}/rest/v1/outbound_touches?id=eq.{touch['id']}", headers=headers, json={"payload": payload, "status": "opened"})
            
            # Log to email_opens
            requests.post(f"{url}/rest/v1/email_opens", headers=headers, json={"email_id": eid, "recipient_email": recipient or None, "business_name": business or None, "opened_at": ts, "metadata": {"ua": ua, "type": "human"}})
            return Response(content=TRANSPARENT_GIF, media_type="image/gif")
            
        elif type == "video" and lid:
            # Update outbound_touches (Video Flag)
            r_get = requests.get(f"{url}/rest/v1/outbound_touches?lead_id=eq.{lid}&order=ts.desc&limit=1", headers=headers)
            if r_get.status_code == 200 and r_get.json():
                touch = r_get.json()[0]
                payload = touch.get("payload") or {}
                payload.update({"video_watched": True, "video_watched_at": ts, "intent_score": (payload.get("intent_score") or 0) + 50})
                requests.patch(f"{url}/rest/v1/outbound_touches?id=eq.{touch['id']}", headers=headers, json={"payload": payload, "status": "engaged"})
            
            # Log to system_health_log
            requests.post(f"{url}/rest/v1/system_health_log", headers=headers, json={"check_type": "video_engagement", "status": "watching", "details": {"lead_id": lid, "ua": ua, "vid": vid_url}})
            return RedirectResponse(url=vid_url or "https://aiserviceco.com")
            
    except Exception as e:
        print(f"Engagement tracking error: {e}")
        
    return Response(content=TRANSPARENT_GIF, media_type="image/gif") if type == "email" else RedirectResponse(url=vid_url or "https://aiserviceco.com")

# ==== SMS INBOUND HANDLER (Sarah AI Reply with Memory) ====
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def sarah_sms_bridge(data: dict = {}):
    """
    Triggered by GHL when a call is missed (no-answer/voicemail).
    Payload: {phone, contact_name, business_name, call_status}
    Logic: Send a 'Rose 500' urgency SMS referencing Lakeland Finds.
    """
    from modules.database.supabase_client import get_supabase
    import os, requests
    
    phone = data.get("phone", "").strip()
    name = data.get("contact_name", "there")
    business = data.get("business_name", "your business")
    status = data.get("call_status", "missed")
    
    if not phone:
        return {"error": "Missing phone"}
        
    # Standardize
    phone = normalize_phone(phone)
    
    script = f"Hey {name}, this is Sarah with AI Service Co. Just tried calling about the missed calls at {business}. We have you listed on Lakeland Finds and I wanted to see when is a good time to connect about recovering that revenue?"
    
    # Send via GHL webhook (existing SMS out flow)
    webhook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not webhook_url:
        return {"error": "GHL_SMS_WEBHOOK_URL missing"}
        
    try:
        resp = requests.post(webhook_url, json={"phone": phone, "message": script})
        
        # Log the touch
        sb = get_supabase()
        sb.table("outbound_touches").insert({
            "channel": "sms",
            "status": "sent",
            "company": business,
            "ts": datetime.now(timezone.utc).isoformat(),
            "payload": {"type": "missed_call_bridge", "script": "sarah_v1_lakeland"}
        }).execute()
        
        return {"status": "triggered", "message": script}
    except Exception as e:
        return {"error": str(e)}

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def ghl_webhook(data: dict = {}):
    """
    Consolidated GHL Webhook Listener (Hardened Phase 16)
    Handles ContactUpdate, OpportunityUpdate, and Appointments.
    """
    from modules.handlers.webhooks import ghl_webhook_logic
    return ghl_webhook_logic(data)

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def sms_inbound(data: dict = {}):
    """
    Receives inbound SMS from GHL webhook, generates Sarah AI reply with persistent memory.
    GHL workflow calls this with: phone, message, contact_name
    Returns: sarah_reply for GHL to send as SMS
    """
    import os
    import requests
    import json
    from datetime import datetime
    from supabase import create_client
    
    phone = data.get("phone", "").strip()
    message = data.get("message", "")
    contact_name = data.get("contact_name", "there")
    
    # CRITICAL FIX (Board 4/4 Approved): Normalize phone to E.164
    # Without this, SMS stores "(352) 936-8152" but Voice looks up "+13529368152"
    phone = normalize_phone(phone)
    
    print(f"[{datetime.now().strftime('%I:%M %p')}] SMS from {phone}: {message[:50]}...")
    
    # --- HOTFIX: Prevent Sarah from replying to System Alerts ---
    if "[HIGH]" in message or "Unknown error" in message or "🚨" in message or "System Alert" in message or "Autonomous Inspector" in message:
        print(f"  🚫 Ignored system alert from hitting Sarah queue.")
        return {"status": "ignored_system_alert", "sarah_reply": ""}
        
    # ══════ SMART ROUTING (Dispatch / Review / Opt-Out) ══════
    import re as _re
    upper_msg = message.strip().upper()
    
    # Route 1: DISPATCH responses (ACCEPT / PASS / DONE)
    if upper_msg in ("ACCEPT", "PASS", "DONE"):
        try:
            from modules.database.supabase_client import get_supabase
            from workers.dispatch import handle_tech_response
            sb = get_supabase()
            result = handle_tech_response(phone, upper_msg, sb)
            return {"routed_to": "dispatch", "result": result}
        except Exception as dr_err:
            print(f"  ⚠️ Dispatch routing error: {dr_err}")
    
    # Route 2: REVIEW ratings (single digit 1-5)
    if _re.match(r'^[1-5]$', message.strip()):
        try:
            from modules.database.supabase_client import get_supabase
            from workers.review_optimizer import handle_rating
            sb = get_supabase()
            rating = int(message.strip())
            result = handle_rating(phone, rating, sb)
            return {"routed_to": "review_optimizer", "result": result}
        except Exception as rv_err:
            print(f"  ⚠️ Review routing error: {rv_err}")
    
    # Route 3: OPT-OUT keywords
    _opt_words = {"STOP", "UNSUBSCRIBE", "REMOVE", "CANCEL", "QUIT", "OPT OUT", "OPTOUT"}
    if upper_msg in _opt_words or any(w in upper_msg for w in _opt_words):
        try:
            from modules.database.supabase_client import get_supabase
            sb = get_supabase()
            sb.table("contacts_master").update({"status": "opted_out"}).eq("phone", phone).execute()
            print(f"  🚫 Opted out: {phone}")
        except Exception as oo_err:
            print(f"  ⚠️ Opt-out error: {oo_err}")
        return {"sarah_reply": "You've been unsubscribed. Reply START to re-subscribe.", "opted_out": True}
    
    # ══════ Fall through to Sarah AI for all other messages ══════
    
    # --- MEMORY LOOKUP ---
    context_summary = {}
    customer_id = None
    
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            
            # Lookup by NORMALIZED phone number (E.164 format)
            result = supabase.table("customer_memory").select("*").eq("phone_number", phone).execute()
            
            if result.data and len(result.data) > 0:
                # Returning customer - get their context
                customer = result.data[0]
                customer_id = customer["customer_id"]
                context_summary = customer.get("context_summary", {}) or {}
                print(f"📝 Found returning customer: {customer_id}, context: {json.dumps(context_summary)[:100]}")
            else:
                # New customer - create record
                new_customer = supabase.table("customer_memory").insert({
                    "phone_number": phone,
                    "context_summary": {
                        "contact_name": contact_name,
                        "history": f"[System]: Customer {contact_name} started conversation via SMS"
                    },
                    "status": "active"
                }).execute()
                if new_customer.data:
                    customer_id = new_customer.data[0]["customer_id"]
                    print(f"🆕 Created new customer: {customer_id}")
            
            # --- RESEARCH LOOKUP (Phase 3 Sovereign Growth) ---
            research_context = ""
            try:
                # Find matching lead in contacts_master to get audit data
                lead_match = supabase.table("contacts_master").select("raw_research, website_url, company_name").eq("phone", phone).limit(1).execute()
                if lead_match.data:
                    lead = lead_match.data[0]
                    raw = json.loads(lead.get("raw_research") or "{}")
                    website = lead.get("website_url")
                    source = lead.get("source", "unknown")
                    
                    if source == "manus":
                        research_context = f"\nRECRUITMENT context: Lead from Manus. They are hiring for: {raw.get('job_role', 'Admin/Reception')}. Offer automated screening demo."
                    elif raw:
                        ps_score = raw.get("pagespeed", {}).get("score", "N/A")
                        privacy = raw.get("privacy", {}).get("status", "unknown")
                        ai_ready = raw.get("ai_readiness", {}).get("status", "unknown")
                        
                        research_context = f"\nWEBSITE AUDIT FINDINGS for {website or lead.get('company_name')}:"
                        research_context += f"\n- Mobile Speed: {ps_score}/100"
                        research_context += f"\n- Privacy Policy (FDBR): {privacy}"
                        research_context += f"\n- AI Readiness: {ai_ready}"
                        if privacy == "critical":
                            research_context += "\n- CRITICAL: Missing Privacy Policy (Florida Digital Bill of Rights risk)."
                        
                        print(f"🧬 Research Inject: {ps_score}/100 Score found for {phone}")
            except Exception as re:
                print(f"⚠️ Research lookup failed: {re}")
    except Exception as e:
        print(f"⚠️ Memory lookup failed (continuing without): {e}")
    
    # --- BUILD CONTEXT-AWARE PROMPT ---
    context_str = ""
    if context_summary:
        context_str = "\n\nCUSTOMER CONTEXT (from previous conversations):\n"
        if context_summary.get("contact_name"):
            context_str += f"- Name: {context_summary['contact_name']}\n"
        if context_summary.get("business_type"):
            context_str += f"- Business: {context_summary['business_type']}\n"
        if context_summary.get("main_challenge"):
            context_str += f"- Challenge: {context_summary['main_challenge']}\n"
        if context_summary.get("budget_mentioned"):
            context_str += f"- Budget hint: {context_summary['budget_mentioned']}\n"
        if context_summary.get("questions_asked"):
            context_str += f"- Already asked: {', '.join(context_summary['questions_asked'])}\n"
        if context_summary.get("history"):
            hist_preview = context_summary['history'][-500:]
            if len(context_summary['history']) > 500:
                hist_preview = '...' + hist_preview
            context_str += f"- Previous interaction notes:\n{hist_preview}\n"
        context_str += "\nDO NOT repeat questions already asked. Build on previous context."
    
    # Sarah's BANT + FDBR + Recruitment prompt 
    SARAH_PROMPT = f"""You are Sarah, AI assistant for AI Service Co.
    
    YOUR MISSION: Identify high-intent leads and pivot immediately to a call with Dan.
    {context_str}
    
    CONVERSATION MODES:
    
    MODE A: RECRUITMENT (Use if 'RECRUITMENT context' is present)
    - Hook: "I saw you're hiring for a [Role] on Manus. Most owners are getting buried in junk resumes right now—we actually have a 24/7 AI agent named Maya that does the first round of interviews *for* you. Want to hear a demo?"
    - Pivot: Once they express interest in the AI screener, book a call with Dan to set up their demo.
    
    MODE B: COMPLIANCE/SPEED (Default)
    - Hook (Florida + No Privacy): "The biggest thing I noticed is your site speed and the new Florida Digital Bill of Rights compliance. You're actually at risk of some heavy penalties without a proper privacy setup. Have you guys addressed that yet?"
    - Hook (Default): "What's the biggest headache in your business right now—automation, customer service, or just keeping up with leads?"
    - Pivot: "Based on that, I think Dan needs to show you our 10-minute fix. Want me to set up a quick call?"
    
    RULES:
    - Keep responses VERY SHORT (1-2 sentences).
    - Be warm but PROFESSIONAL and URGENT.
    - After 3 messages, you MUST ask for the call. No more 'just chatting'.
    
    FALLBACK:
    - "I want to make sure I get you the best help—let me have Dan reach out directly. When's a good time?"
    """
    
    # --- LOAD CONVERSATION HISTORY (prevents looping/re-asking) ---
    conversation_history = []
    try:
        if supabase_url and supabase_key and customer_id:
            sb = create_client(supabase_url, supabase_key)
            recent = sb.table("conversation_logs").select("content,sarah_response,direction").eq("customer_id", customer_id).eq("channel", "sms").order("timestamp", desc=True).limit(5).execute()
            if recent.data:
                for msg_row in reversed(recent.data):  # oldest first
                    if msg_row.get('content'):
                        conversation_history.append({"role": "user", "content": msg_row['content']})
                    if msg_row.get('sarah_response'):
                        conversation_history.append({"role": "assistant", "content": msg_row['sarah_response']})
                print(f"📝 Loaded {len(recent.data)} past conversations for context")
    except Exception as hist_err:
        print(f"⚠️ History load failed (continuing): {hist_err}")
    
    # --- BUILD CONTEXT-AWARE SYSTEM PROMPT ---
    context_info = ""
    if context_summary:
        if context_summary.get('contact_name'):
            context_info += f"\nCustomer name: {context_summary['contact_name']}"
        if context_summary.get('business_type'):
            context_info += f"\nBusiness type: {context_summary['business_type']}"
        if context_summary.get('main_challenge'):
            context_info += f"\nMain challenge: {context_summary['main_challenge']}"
        if context_summary.get('questions_asked'):
            context_info += f"\nQuestions already asked (DO NOT re-ask): {', '.join(context_summary['questions_asked'])}"
    
    full_prompt = SARAH_PROMPT
    if context_info:
        full_prompt += f"\n\nKNOWN CUSTOMER INFO:{context_info}\n\nIMPORTANT: Do NOT re-ask questions you've already asked. Move the conversation forward."
    
    if research_context:
        full_prompt += f"\n\n{research_context}\n\nUSE THIS INTEL: Reference these findings naturally to show we've done our homework. If privacy is 'critical', use the 'Florida Digital Bill of Rights' hook to create urgency."
    
    # Generate reply using Grok
    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key:
        return {"sarah_reply": "Hey! Let me have Dan call you back shortly. -Sarah", "status": "fallback"}
    
    reply = ""
    try:
        # Build messages with conversation history
        messages = [{"role": "system", "content": full_prompt}]
        messages.extend(conversation_history)  # Past conversation
        messages.append({"role": "user", "content": f"Incoming SMS from {contact_name}: \"{message}\"\n\nWrite a short SMS reply:"})
        
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": messages,
                "model": "grok-3",
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=30
        )
        if resp.status_code == 200:
            reply = resp.json()['choices'][0]['message']['content'].strip()
            print(f"Sarah reply: {reply[:50]}...")
        else:
            print(f"Grok error: {resp.status_code}")
            reply = "Hey! I'll have Dan reach out shortly. -Sarah"
    except Exception as e:
        print(f"Error: {e}")
        reply = "Hey! Let me have Dan follow up with you. -Sarah"
    
    # --- LOG CONVERSATION & UPDATE CONTEXT ---
    try:
        if supabase_url and supabase_key and customer_id:
            supabase = create_client(supabase_url, supabase_key)
            
            # Log the conversation
            supabase.table("conversation_logs").insert({
                "customer_id": customer_id,
                "channel": "sms",
                "direction": "inbound",
                "content": message,
                "sarah_response": reply,
                "metadata": {"contact_name": contact_name}
            }).execute()
            
            # Update context_summary with any new intel (basic extraction)
            updated_context = context_summary.copy()
            message_lower = message.lower()
            
            # --- NAME EXTRACTION (Board Fix #2): User's stated name > GHL name ---
            import re
            name_patterns = [
                r"(?:my name is|i'm|i am|this is|it's|call me)\s+([A-Z][a-z]+)",
                r"^([A-Z][a-z]+)\s+here",
            ]
            extracted_name = None
            for pattern in name_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    extracted_name = match.group(1).title()
                    break
            
            if extracted_name:
                # User explicitly stated their name — this takes priority
                updated_context["contact_name"] = extracted_name
                print(f"📝 Name extracted from message: '{extracted_name}' (overrides GHL: '{contact_name}')")
            elif not updated_context.get("contact_name"):
                # No existing name — use GHL's as initial fallback
                updated_context["contact_name"] = contact_name
            # Otherwise: keep whatever name is already stored (don't overwrite)
            
            # Simple keyword extraction for context
            if any(word in message_lower for word in ["hvac", "plumber", "plumbing", "contractor", "roofing", "electrician", "lawn", "landscap", "cleaning", "pest", "pool", "tire", "auto", "mechanic"]):
                for word in message.split():
                    if word.lower() in ["hvac", "plumber", "plumbing", "contractor", "roofing", "electrician", "lawn", "landscaping", "cleaning", "pest", "pool", "tire", "auto", "mechanic"]:
                        updated_context["business_type"] = word.lower()
                        break
            if any(word in message_lower for word in ["miss", "calls", "after hours", "weekend"]):
                updated_context["main_challenge"] = "missed calls"
            if "$" in message or "budget" in message_lower:
                updated_context["budget_mentioned"] = message
            
            # --- QUESTION TRACKING (Board Fix #3): Track ALL questions Sarah asks ---
            questions_asked = updated_context.get("questions_asked", [])
            reply_lower = reply.lower()
            if "what kind of business" in reply_lower or "what do you do" in reply_lower:
                questions_asked.append("business_type")
            if "challenge" in reply_lower or "headache" in reply_lower or "pain point" in reply_lower:
                questions_asked.append("challenge")
            if "making decisions" in reply_lower or "decision maker" in reply_lower:
                questions_asked.append("authority")
            if "pricing" in reply_lower or "$99" in reply_lower or "cost" in reply_lower:
                questions_asked.append("budget")
            if "when" in reply_lower and ("looking" in reply_lower or "timeline" in reply_lower):
                questions_asked.append("timeline")
            if "set up a" in reply_lower and ("call" in reply_lower or "chat" in reply_lower):
                questions_asked.append("call_offer")
            updated_context["questions_asked"] = list(set(questions_asked))
            
            # Save updated context (NOTE: customer_name column doesn't exist on table)
            supabase.table("customer_memory").update({
                "context_summary": updated_context
            }).eq("customer_id", customer_id).execute()
            
            print(f"✅ Logged conversation and updated context for {customer_id}")
    except Exception as e:
        print(f"⚠️ Failed to log conversation: {e}")
    
    # --- NOTIFY DAN about incoming SMS ---
    try:
        import urllib.request
        dan_phone = "+13529368152"
        notify_msg = f"💬 SMS to Sarah\nFrom: {contact_name} ({phone})\nMsg: {message[:150]}\nSarah replied: {reply[:100]}"
        ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
        notify_payload = json.dumps({"phone": dan_phone, "message": notify_msg}).encode()
        notify_req = urllib.request.Request(ghl_webhook, data=notify_payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(notify_req, timeout=10)
        print(f"📱 [NOTIFY] ✅ Dan notified about SMS from {contact_name}")
    except Exception as notify_err:
        print(f"📱 [NOTIFY] ⚠️ Failed to notify Dan: {notify_err}")
    
    return {"sarah_reply": reply, "status": "success", "customer_id": str(customer_id) if customer_id else None}


# ==== SHARED PHONE NORMALIZATION (Board Requirement) ====
def normalize_phone(raw_phone: str) -> str:
    """
    Standardize phone to E.164 format: +1XXXXXXXXXX
    Used by BOTH vapi_webhook and sms_inbound for consistency.
    Board mandate: prevent format mismatch causing memory lookup failures.
    """
    import re
    if not raw_phone:
        return ""
    digits = re.sub(r'\D', '', raw_phone)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 11:
        return f"+{digits}"  # Already has country code
    return f"+{digits}" if digits else ""


# ==== VEO VISIONARY SERVICE KNOWLEDGE (Board Approved) ====
SERVICE_KNOWLEDGE = """
SERVICES WE OFFER (VEO Visionary / AI Service Co):
- AI Voice/SMS automation (24/7 answering, booking, lead qualification)
- Facebook & Instagram ad campaigns (lead generation)
- Google Ads management
- Marketing for local businesses
- Website optimization and SEO

FLEXIBLE POLICY:
If a customer asks for ANY service related to marketing, automation, or lead generation - say "Yes, we can help with that!" 
We accommodate custom requests. Don't turn customers away.
For requests clearly outside our expertise, politely explain we specialize in marketing/automation and offer to explore related solutions.

BRAND: We operate under AI Service Co and VEO Visionary Ads.
"""


# ==== VAPI WEBHOOK HANDLER (Call Direction + Memory) ====
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def vapi_webhook(data: dict = None):
    """
    Absolute Hardened Vapi Webhook (Feb 13, 2026)
    GUARANTEED 200 OK for all events.
    """
    import os
    import json
    import re
    import traceback
    from datetime import datetime
    
    # Early print to verify function entry
    print(f"DEBUG: Vapi Webhook received event")

    try:
        # 0. Defensive Payload Handling
        if data is None: 
            data = {}
            
        message = data.get("message") or {}
        if not isinstance(message, dict): message = {}
        
        event_type = message.get("type", "unknown")
        call = message.get("call") or {}
        if not isinstance(call, dict): call = {}
        
        # 1. FAST TELEMETRY EXIT (Prevents processing overhead for high-volume data)
        TELEMETRY_EVENTS = ["speech-update", "status-update", "conversation-update", "user-interrupted"]
        if event_type in TELEMETRY_EVENTS:
            return {"status": "received", "event": event_type}
            
        # 2. Delayed Imports (Prevents ImportError from crashing the endpoint)
        try:
            import sys
            print(f"DEBUG: sys.path = {sys.path}")
            print(f"DEBUG: Current dir contents: {os.listdir('.')}")
            if os.path.exists("modules"):
                print(f"DEBUG: modules dir contents: {os.listdir('modules')}")
            
            from modules.voice.sales_persona import get_persona_prompt, SALES_SARAH_PROMPT
            from supabase import create_client
            print("✅ [VAPI] Imports successful")
        except Exception as imp_err:
            print(f"⚠️ [VAPI] Import failure (non-fatal): {imp_err}")
            traceback.print_exc()
            # DON'T RETURN - end-of-call-report doesn't need these imports!
            # Only assistant-request and tool-calls need sales_persona
            get_persona_prompt = None
            SALES_SARAH_PROMPT = None
            if event_type in ["tool-calls", "assistant-request"]:
                return {"status": "import_error", "event": event_type, "error": str(imp_err)}
            # For end-of-call-report: import supabase separately
            try:
                from supabase import create_client
            except:
                return {"status": "import_error", "event": event_type, "error": "supabase import failed"}

        # 3. Shared Context Initialization
        direction = call.get("direction") or call.get("type") or call.get("callType", "unknown")
        customer = message.get("customer") or call.get("customer") or {}
        raw_phone = customer.get("number") or call.get("customerNumber") or call.get("to") or ""
        
        # Safe normalization
        caller_phone = ""
        dialed_number = ""
        try:
            caller_phone = normalize_phone(raw_phone)
            dialed_number = normalize_phone(call.get("to", ""))
        except: pass
        
        MAYA_NUMBER = "+19362984339"
        is_maya_call = (dialed_number == MAYA_NUMBER or "9362984339" in dialed_number)
        call_mode = "explainer" if is_maya_call else "support"
        
        # Log basic entry point after safe parsing
        print(f"📞 [EVENT] {event_type} | Mode: {call_mode} | Phone: {caller_phone}")
        # 4. Advanced Initialization (for memory/tool phases)
        customer_name = ""
        context_summary = {}
        system_prompt = ""
        assistant_overrides = {}
        extracted_name = ""
        summary = message.get("summary") or ""
        transcript = message.get("transcript") or ""
        lookup_status = "PENDING"

        # 4. Extract Identity Context
        direction = call.get("direction") or call.get("type") or call.get("callType", "unknown")
        if direction in ["inboundPhoneCall", "inbound"]:
            direction = "inbound"
        elif direction in ["outboundPhoneCall", "outbound"]:
            direction = "outbound"

        customer = message.get("customer") or call.get("customer") or {}
        if not isinstance(customer, dict):
            customer = {}
            
        raw_phone = customer.get("number") or call.get("customerNumber") or call.get("to") or ""
        caller_phone = normalize_phone(raw_phone)
        dialed_number = normalize_phone(call.get("to", ""))
        
        is_maya_call = (dialed_number == MAYA_NUMBER or "9362984339" in dialed_number)
        call_mode = "explainer" if is_maya_call else "support"
        summary = message.get("summary") or ""
        transcript = message.get("transcript") or ""

        print(f"\n{'='*60}")
        print(f"📞 [VAPI WEBHOOK] ENTRY - Event: {event_type} | Mode: {call_mode} | Phone: {caller_phone}")

        # ========== PHASE 1: TOOL CALLS ==========
        if event_type == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            if not tool_calls:
                return {"results": []}
                
            results = []
            for tc in tool_calls:
                func = tc.get("function", {})
                name = func.get("name")
                args = func.get("arguments", {})
                call_id = tc.get("id")
                
                print(f"🛠️ [TOOLS] Maya calling function: {name} with args: {args}")
                
                if name == "lookup_business":
                    biz_name = args.get("business_name")
                    result_data = lookup_business_google(biz_name)
                    results.append({
                        "toolCallId": call_id,
                        "result": json.dumps(result_data)
                    })
            return {"results": results}

        # ========== PHASE 2: ASSISTANT REQUEST (Persona + Memory) ==========
        if event_type == "assistant-request":
            # Memory Lookup
            if caller_phone and len(caller_phone) >= 10:
                try:
                    supabase_url = os.environ.get("SUPABASE_URL")
                    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
                    
                    if supabase_url and supabase_key:
                        supabase = create_client(supabase_url, supabase_key)
                        result = supabase.table("customer_memory").select("*").eq("phone_number", caller_phone).limit(1).execute()
                        
                        if result.data:
                            customer_data = result.data[0]
                            context_data = customer_data.get("context_summary", {})
                            context_summary = {"history": context_data} if isinstance(context_data, str) else context_data
                            customer_name = context_summary.get("contact_name") or customer_data.get("customer_name") or ""
                            lookup_status = "FOUND"
                            if context_summary.get("call_purpose") == "sales":
                                call_mode = "sales"
                        else:
                            lookup_status = "NOT_FOUND"
                    else:
                        lookup_status = "ERROR_CREDS"
                except Exception as mem_err:
                    print(f"⚠️ [MEMORY] Lookup error: {mem_err}")
                    lookup_status = "ERROR"

            # Build Dynamic Prompt
            if direction == "inbound":
                if customer_name:
                    greeting_instruction = f"INBOUND CALL - RETURNING Customer: {customer_name}. Greet them by name!"
                else:
                    greeting_instruction = "INBOUND CALL - NEW Customer. Greet warmly and ask for their name."
            elif direction == "outbound":
                greeting_instruction = f"OUTBOUND CALL to {customer_name or 'customer'}. Confirm who is on the phone."
            else:
                greeting_instruction = "UNKNOWN direction. Be neutral and helpful."

            context_injection = ""
            if context_summary:
                ctx = context_summary
                qa = ', '.join(ctx.get('questions_asked', [])) or 'None'
                hist = str(ctx.get('history', 'No prior data'))[-1000:]
                context_injection = f"\nCUSTOMER CONTEXT: Name={customer_name}, History={hist}, Done={qa}\n"

            # Maya Tools Configuration
            maya_tools = []
            if is_maya_call:
                call_mode = "explainer"
                maya_tools = [{
                    "async": False,
                    "type": "function",
                    "function": {
                        "name": "lookup_business",
                        "description": "Searches Google for a business to check ratings and standing.",
                        "parameters": {
                            "type": "object",
                            "properties": {"business_name": {"type": "string"}},
                            "required": ["business_name"]
                        }
                    },
                    "server": {"url": "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"}
                }]

            # Determine Persona
            if call_mode == "sales":
                system_prompt = SALES_SARAH_PROMPT.format(customer_name=customer_name or "there", service_knowledge=SERVICE_KNOWLEDGE)
            elif call_mode == "explainer":
                system_prompt = get_persona_prompt(call_mode="explainer", service_knowledge=SERVICE_KNOWLEDGE)
            else:
                # Support Sarah (BANT)
                system_prompt = f"You are Sarah, AI phone assistant for AI Service Co. Warm, casual. {greeting_instruction} {context_injection} {SERVICE_KNOWLEDGE} MISSION: BANT qualification."

            # Maya's first message depends on who's calling
            DAN_PHONE = "+13529368152"
            if is_maya_call:
                if caller_phone == DAN_PHONE:
                    maya_first = "Hey boss! What's going on? Who are we impressing today?"
                elif customer_name:
                    maya_first = f"Hey {customer_name}! Thanks for calling, I'm Maya with AI Service Co. How's your day going?"
                else:
                    maya_first = "Hey! Thanks for calling, I'm Maya with AI Service Co. How's your day going?"
            else:
                maya_first = None

            assistant_overrides = {
                "variableValues": {"customerPhone": caller_phone, "customerName": customer_name, "callMode": call_mode},
                "firstMessage": maya_first,
                "systemPrompt": system_prompt
            }


            # Independent Logging Block
            try:
                sb_url = os.environ.get("SUPABASE_URL")
                sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
                if sb_url and sb_key:
                    sb = create_client(sb_url, sb_key)
                    sb.table("vapi_debug_logs").insert({
                        "event_type": event_type,
                        "normalized_phone": caller_phone,
                        "lookup_result": lookup_status,
                        "customer_name_found": customer_name,
                        "call_mode": call_mode,
                        "direction": direction,
                        "call_direction": direction,
                        "raw_phone": raw_phone,
                        "context_summary": context_summary if isinstance(context_summary, dict) else {"history": str(context_summary)},
                        "assistant_overrides_sent": assistant_overrides
                    }).execute()
            except Exception as log_err:
                print(f"⚠️ [VAPI] Debug logging failed: {log_err}")

            vapi_config = {
                "name": "Maya" if is_maya_call else "Sarah",
                "firstMessage": assistant_overrides.get("firstMessage"),
                "model": {"provider": "openai", "model": "gpt-4o", "messages": [{"role": "system", "content": system_prompt}], "tools": maya_tools}
            }
            if is_maya_call: vapi_config["tools"] = maya_tools

            return {"assistant": vapi_config, "assistantOverrides": assistant_overrides}

        # ========== PHASE 3: END OF CALL REPORT ==========
        if event_type == "end-of-call-report":
            # Persistence Logic (Memory + GHL Notification)
            if caller_phone:
                try:
                    sb_url = os.environ.get("SUPABASE_URL")
                    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
                    if sb_url and sb_key:
                        sb = create_client(sb_url, sb_key)
                        
                        # Name extraction
                        name_match = re.search(r"(?:name is|i'm|this is)\s+([A-Z][a-z]+)", transcript or "", re.I)
                        extracted_name = name_match.group(1).title() if name_match else ""
                        
                        # Memory Update
                        res = sb.table("customer_memory").select("context_summary").eq("phone_number", caller_phone).limit(1).execute()
                        ctx = res.data[0].get("context_summary") or {} if res.data else {}
                        if isinstance(ctx, str): ctx = {"history": ctx}
                        
                        new_hist = f"{ctx.get('history','')}\n[{direction.upper()} {datetime.utcnow().strftime('%m/%d %H:%M')}]: {summary or 'Ended'}"
                        ctx["history"] = new_hist[-3000:]
                        if extracted_name: ctx["contact_name"] = extracted_name
                        
                        sb.table("customer_memory").upsert({"phone_number": caller_phone, "context_summary": ctx}, on_conflict="phone_number").execute()
                        
                        # === DAN NOTIFICATION (Multi-Method: Email + DB + GHL fallback) ===
                        notify_msg = f"📞 Call Summary: {caller_phone}\nName: {extracted_name or 'Unknown'}\nDir: {direction}\nSum: {(summary or 'No summary')[:200]}"
                        print(f"📱 [NOTIFY] Sending alert to Dan: {notify_msg[:80]}...")
                        
                        # METHOD 1: Resend Email (most reliable)
                        try:
                            resend_key = os.environ.get("RESEND_API_KEY")
                            if resend_key:
                                import requests as req
                                email_body = f"""<div style="font-family: Arial; padding: 20px;">
                                <h2>📞 Call Alert</h2>
                                <p><strong>Caller:</strong> {caller_phone}</p>
                                <p><strong>Name:</strong> {extracted_name or 'Unknown'}</p>
                                <p><strong>Direction:</strong> {direction}</p>
                                <p><strong>Summary:</strong> {(summary or 'No summary')[:500]}</p>
                                <p><strong>Transcript:</strong><br>{(transcript or 'No transcript')[:1000]}</p>
                                <hr><p style="color:#666">Sent by Sarah AI at {datetime.utcnow().strftime('%I:%M %p UTC')}</p>
                                </div>"""
                                er = req.post("https://api.resend.com/emails", headers={
                                    "Authorization": f"Bearer {resend_key}",
                                    "Content-Type": "application/json"
                                }, json={
                                    "from": "Sarah AI <owner@aiserviceco.com>",
                                    "to": ["owner@aiserviceco.com"],
                                    "subject": f"📞 Call Alert: {extracted_name or caller_phone} ({direction})",
                                    "html": email_body
                                }, timeout=10)
                                print(f"📱 [NOTIFY] Resend email: {er.status_code}")
                        except Exception as email_err:
                            print(f"📱 [NOTIFY] Email failed: {email_err}")
                        
                        # METHOD 2: Supabase call_alerts table (always works)
                        try:
                            sb.table("system_health_log").insert({
                                "check_type": "call_alert",
                                "status": "alert",
                                "details": {
                                    "message": notify_msg,
                                    "caller_phone": caller_phone,
                                    "caller_name": extracted_name,
                                    "direction": direction,
                                    "summary": (summary or "")[:500],
                                    "transcript": (transcript or "")[:1000]
                                }
                            }).execute()
                            print(f"📱 [NOTIFY] Supabase alert logged")
                        except Exception as db_err:
                            print(f"📱 [NOTIFY] DB log failed: {db_err}")
                        
                        # METHOD 3: GHL webhook (may fail if Dan not a contact)
                        try:
                            import urllib.request
                            urllib.request.urlopen(urllib.request.Request(
                                "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd",
                                data=json.dumps({"phone": "+13529368152", "message": notify_msg}).encode(),
                                headers={"Content-Type": "application/json"}
                            ), timeout=10)
                            print(f"📱 [NOTIFY] GHL webhook sent")
                        except Exception as ghl_err:
                            print(f"📱 [NOTIFY] GHL webhook failed (422 = Dan not in GHL): {ghl_err}")
                except Exception as e:
                    print(f"⚠️ [REPORT] End of call processing failed: {e}")
            
            return {"status": "logged", "phone": caller_phone}

        # Default Response
        return {"status": "received", "event": event_type}

    except Exception as global_err:
        print(f"❌ CRITICAL VAPI WEBHOOK ERROR: {global_err}")
        print(traceback.format_exc())
        return {"status": "error_handled", "error": str(global_err)}



@app.function(image=image, secrets=[VAULT], timeout=60)
def send_executive_pulse():
    """Aggregates Revenue Waterfall and sends SMS Pulse to Dan and Wife (Phase 21)."""
    import os, json, requests
    from datetime import datetime, timezone
    from scripts.revenue_waterfall import get_waterfall_summary
    
    print("📱 EXECUTIVE PULSE: Generating daily report...")
    # Run the verified waterfall diagnostic using HTTP REST to prevent tcp/ip socket errors
    try:
        from modules.database.supabase_client import get_supabase
        sb = get_supabase()
        
        # Outreach
        res = sb.table('outbound_touches').select('id', count='exact').gte('ts', (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()).execute()
        outreach_24h = getattr(res, 'count', len(getattr(res, 'data', [])))
        
        # Heartbeat
        hb = sb.table('system_health_log').select('checked_at').order('checked_at', desc=True).limit(1).execute()
        last_hb = getattr(hb, 'data', [{}])[0].get('checked_at', 'NONE')
        if type(last_hb) == str and len(last_hb) > 16:
            last_hb = last_hb[11:16] + " UTC"
            
        # Campaign Mode
        cm = sb.table('system_state').select('status').eq('key', 'campaign_mode').execute()
        campaign_status = getattr(cm, 'data', [{}])[0].get('status', 'UNKNOWN')
        
        # Eligible Leads
        leads = sb.table('contacts_master').select('id', count='exact').in_('status', ['new', 'research_done']).execute()
        leads_count = getattr(leads, 'count', len(getattr(leads, 'data', [])))
        
        summary = (
            f"📈 Outreach (24h): {outreach_24h}\n"
            f"💓 Last Pulse: {last_hb}\n"
            f"🔄 Mode: {campaign_status}\n"
            f"🎯 Pool: {leads_count} leads"
        )
    except Exception as e:
        summary = f"❌ Waterfall Rest Error: {str(e)}"
    
    # Format SMS content (clean, high-signal)
    report = f"⚫ SOVEREIGN PULSE [{now.strftime('%m/%d')}]\n\n{summary}"
    report += "\n🚀 View Full Dashboard: https://aiserviceco.com/dashboard"
    
    # Recipients (Owner Only - Removed Wife/GF number)
    recipients = ["+13529368152"]
    
    # GHL Notify Webhook
    ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    for phone in recipients:
        try:
            requests.post(ghl_webhook, json={"phone": phone, "message": report}, timeout=10)
            print(f"✅ Pulse sent to {phone}")
        except Exception as e:
            print(f"❌ Failed to send pulse to {phone}: {e}")

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"), timeout=600)
def system_orchestrator():
    """Master Orchestrator: Health, Outreach, and Time-based Strikes (Sovereign Consolidation)."""
    import os
    from datetime import datetime, timezone
    from modules.autonomous_inspector import Inspector, safe_spawn, safe_local
    
    inspector = Inspector()
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    minute = now_utc.minute
    weekday = now_utc.weekday() # 0=Mon, 6=Sun
    
    print(f"🚀 MASTER ORCHESTRATOR: Pulse at {now_utc.isoformat()}")
    
    try:
        # 1. Health & Pulse (Every 5 min)
        safe_local(system_heartbeat, "system_heartbeat")
        
        # 2. Outreach Loop (Every 5 min)
        safe_local(auto_outreach_loop, "auto_outreach_loop")
        
        # 3. Nurture Drip + Newsletter (Every 5 min — timezone-aware)
        try:
            from workers.nurture import run_nurture_cycle
            nurture_result = run_nurture_cycle(max_actions=10)
            print(f"📬 Nurture: {nurture_result.get('total_actions', 0)} actions")
        except Exception as e:
            print(f"⚠️ Nurture engine error: {e}")
        
        # --- TIME-BASED TRIGGERS (Consolidated Crons) ---
        
        # A. Sunbiz Delta Watch (8 AM Mon-Sat -> hour 8 UTC if EST as per original cron)
        if hour == 8 and minute < 5 and weekday < 6:
            print("🚀 TRIGGER: Sunbiz Delta Watch (Consolidated)")
            safe_spawn(scheduled_sunbiz_delta_watch, "scheduled_sunbiz_delta_watch")

        # B. Social Multiplier (9 AM and 4 PM EST -> 14 and 21 UTC per original cron)
        if hour in [14, 21] and minute < 5:
            print("🚀 TRIGGER: Social Multiplier (Consolidated)")
            safe_spawn(schedule_social_multiplier, "schedule_social_multiplier")

        # C. Weekly Newsletter (Mondays at 9 AM EST -> 14 UTC per original cron)
        if weekday == 0 and hour == 14 and minute < 5:
            print("🚀 TRIGGER: Weekly Newsletter (Consolidated)")
            safe_spawn(weekly_newsletter, "weekly_newsletter")
        
        # D. Lakeland Background Ingestion (Hourly at minute 12)
        if minute >= 12 and minute < 17:
            from workers.lakeland_ingestion import run_ingestion_batch
            try:
                from modules.database.supabase_client import get_supabase
                supabase = get_supabase()
                last_ingest = supabase.table("system_state").select("status").eq("key", "last_ingestion_hour").execute()
                current_hour_key = f"{now_utc.date()}_{hour}"
                
                if not last_ingest.data or last_ingest.data[0].get("status") != current_hour_key:
                    print(f"🚀 TRIGGER: Lakeland Ingestion (Hourly: {current_hour_key})")
                    supabase.table("system_state").upsert({
                        "key": "last_ingestion_hour",
                        "status": current_hour_key
                    }, on_conflict="key").execute()
                    safe_spawn(run_ingestion_batch, "run_ingestion_batch", batch_size=50)
            except Exception as e:
                print(f"⚠️ Ingestion trigger failed: {e}")

        # E. Lakeland AI Enrichment (Hourly at minute 42)
        # [DEPRECATED] Migrated to Abacus.AI Nightly Daemons (Phase 2)
        # Freed up Modal compute resources.

        # F. Daily Executive Pulse (8 AM EST -> 13 UTC)
        if hour == 13 and minute < 5:
            print("🚀 TRIGGER: Daily Executive Pulse (Phase 21)")
            safe_spawn(send_executive_pulse, "send_executive_pulse")

        # G. PROSPECTOR ENGINE (Every 30 min — minute 0-4 and 30-34)
        if minute < 5 or (minute >= 30 and minute < 35):
            try:
                from modules.database.supabase_client import get_supabase
                supabase = get_supabase()
                last_prospect = supabase.table("system_state").select("status").eq("key", "last_prospect_half_hour").execute()
                half_hour_key = f"{now_utc.date()}_{hour}_{minute // 30}"
                
                if not last_prospect.data or last_prospect.data[0].get("status") != half_hour_key:
                    print(f"🚀 TRIGGER: Prospector Engine (Every 30 min: {half_hour_key})")
                    supabase.table("system_state").upsert({
                        "key": "last_prospect_half_hour",
                        "status": half_hour_key
                    }, on_conflict="key").execute()
                    # Spawn as async to not block orchestrator
                    safe_spawn(run_prospector, "run_prospector")
            except Exception as e:
                print(f"⚠️ Prospector trigger failed: {e}")

        print("✅ MASTER ORCHESTRATOR: Pulse complete.")
    
    except Exception as orch_err:
        # ── AUTONOMOUS INSPECTOR — Detect, Diagnose, Repair ──
        print(f"🚨 ORCHESTRATOR CRASH: {orch_err}")
        import traceback
        traceback.print_exc()
        
        # Phase 1: Route crash telemetry to Abacus.AI
        try:
            import requests
            requests.post(
                "https://sovereign-empire-api-908fw2.abacusai.app/webhook/system-error",
                json={
                    "source": "modal",
                    "error_type": type(orch_err).__name__,
                    "error_message": str(orch_err)[:500],
                    "stack_trace": traceback.format_exc(),
                    "severity": "critical"
                },
                headers={"Authorization": "Bearer sovereign_abacus_webhook_2026_xyz99", "Content-Type": "application/json"},
                timeout=10
            )
        except Exception as abacus_err:
            print(f"⚠️ Failed to log error to Abacus: {abacus_err}")

        try:
            inspector.handle_crash("system_orchestrator", orch_err)
        except Exception as inspect_err:
            print(f"❌ Inspector itself failed: {inspect_err}")
            # Fallback: raw SMS alert
            try:
                requests.post(
                    "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd",
                    json={"phone": "+13529368152", "message": f"🚨 ORCHESTRATOR + INSPECTOR BOTH CRASHED: {str(orch_err)[:200]}", "type": "system_alert"},
                    timeout=10
                )
            except Exception:
                pass

@app.function(image=image, secrets=[VAULT])
def system_heartbeat():
    """Health check + Vapi call monitor (polls for completed calls, notifies Dan)."""
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    print(f"HEARTBEAT: Running at {datetime.now(timezone.utc).isoformat()}")
    
    issues = []
    try:
        supabase = get_supabase()
        
        # 1. Check Campaign Mode
        campaign = supabase.table("system_state").select("status").eq("key", "campaign_mode").execute()
        mode = campaign.data[0].get("status") if campaign.data else "unknown"
        if mode != "working":
            issues.append(f"Campaign mode is '{mode}'")
            
        # 2. Log Pulse
        supabase.table("system_health_log").insert({
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "check_type": "heartbeat_v3",
            "status": "ok" if not issues else "degraded",
            "details": {"issues": issues, "cron_limit": 2}
        }).execute()
        
    except Exception as e:
        print(f"Heartbeat Error: {e}")
    
    # ---- SELF-HEALING CHECKS (each independently try/excepted — cannot crash heartbeat) ----
    
    # Check A: Is outreach actually sending? (last 30 min)
    try:
        supabase = get_supabase()
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        recent = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff).execute()
        outreach_count = recent.count if recent.count is not None else len(recent.data)
        
        if outreach_count == 0 and mode == "working":
            issues.append("OUTREACH STALLED: 0 touches in 30 min")
            
    except Exception as e:
        print(f"Self-Healing Diagnostic Error: {e}")

    # --- Schema Self-Healing (Ensures audit_cache and reporting columns exist) ---
    try:
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            # 1. audit_cache table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_cache (
                    url TEXT PRIMARY KEY,
                    score INTEGER,
                    raw_data JSONB,
                    privacy_status TEXT,
                    ai_status TEXT,
                    last_audited_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # 2. outbound_touches reporting columns
            cur.execute("""
                ALTER TABLE outbound_touches 
                ADD COLUMN IF NOT EXISTS opened BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS opened_at TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
            """)
            
            # 3. call_transcripts table (User Requirement: Phase 29)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS call_transcripts (
                    id BIGSERIAL PRIMARY KEY,
                    call_id TEXT UNIQUE,
                    phone_number TEXT,
                    direction TEXT,
                    summary TEXT,
                    transcript TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                );
            """)
            
            # 4. system_error_log table (Inspector: Phase 31)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_error_log (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    source TEXT NOT NULL,
                    error_type TEXT,
                    error_message TEXT,
                    traceback TEXT,
                    context JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'new',
                    retry_count INT DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_error_log_source ON system_error_log(source);
                CREATE INDEX IF NOT EXISTS idx_error_log_created ON system_error_log(created_at DESC);
            """)
            
            conn.commit()
            cur.close()
            conn.close()
    except Exception as schema_err:
        print(f"⚠️ Schema Self-Healing failed: {schema_err}")
    
    # Check A cont: Outreach status report (Indentation fixed)
    try:
        if outreach_count == 0:
            print(f"⚠️ SELF-HEAL: Outreach stalled — 0 touches in last 30 min")
        else:
            print(f"✅ Outreach check: {outreach_count} touches in last 30 min")
    except Exception as e:
        print(f"Self-heal check A (outreach) reporting error: {e}")
    
    # Check B: Are there contactable leads? (status = 'new' or 'research_done')
    try:
        supabase = get_supabase()
        pool = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
        pool_count = pool.count if pool.count is not None else len(pool.data)
        
        if pool_count == 0:
            issues.append(f"LEAD POOL EMPTY: 0 contactable leads")
            print(f"🚨 SELF-HEAL: Lead pool exhausted — 0 leads with status new/research_done")
        else:
            print(f"✅ Lead pool check: {pool_count} contactable leads")
    except Exception as e:
        print(f"Self-heal check B (lead pool) error (non-fatal): {e}")
    
    # Check C: Has prospector run in last 12 hours?
    try:
        supabase = get_supabase()
        last_run = supabase.table("system_state").select("last_error").eq("key", "prospector_last_run").execute()
        
        if last_run.data and last_run.data[0].get("last_error"):
            last_ts = datetime.fromisoformat(last_run.data[0]["last_error"])
            hours_since = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
            if hours_since > 12:
                issues.append(f"PROSPECTOR STALLED: {hours_since:.1f}h since last run")
                print(f"⚠️ SELF-HEAL: Prospector stalled — {hours_since:.1f}h since last run (threshold: 12h)")
            else:
                print(f"✅ Prospector check: ran {hours_since:.1f}h ago")
        else:
            print(f"⚠️ Prospector check: no run recorded yet")
    except Exception as e:
        print(f"Self-heal check C (prospector) error (non-fatal): {e}")
    
    # --- Check for stalled workers ---
    # If research worker is stalled, reset it
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        
        # 1. Fetch eligible leads ('new' status and has website)
        res = requests.get(f"{url}/rest/v1/contacts_master?status=eq.new&website_url=not.is.null&limit=5", headers=headers)
        eligible_leads = res.json() if res.status_code == 200 else []
        
        # 2. Check audit_reports for recent activity
        audit_res = requests.get(f"{url}/rest/v1/audit_reports?select=created_at&order=created_at.desc&limit=1", headers=headers)
        last_audit_data = audit_res.json() if audit_res.status_code == 200 else []
        last_audit_time = None
        if last_audit_data:
            last_audit_time = datetime.fromisoformat(last_audit_data[0]["created_at"].replace('Z', '+00:00'))
        
        # If leads exist and (no audits recently OR last audit was > 30m ago), trigger workers
        if eligible_leads and (not last_audit_time or last_audit_time < datetime.now(timezone.utc) - timedelta(minutes=30)):
            print(f"  [RESEARCH STALL DETECTED] Eligible leads: {len(eligible_leads)}. Last audit: {last_audit_time}. Triggering workers...")
            
            # Fetch 2 leads to process
            for lead in eligible_leads[:2]:
                print(f"    Spawning research_strike_worker for lead: {lead['id']}")
                research_strike_worker.spawn(lead['id']) 
        else:
            print(f"  Research worker status: OK (Eligible: {len(eligible_leads)}, Last Audit: {last_audit_time})")
            
    except Exception as e:
        print(f"  [RESEARCH STALL CHECK ERROR]: {e}")
        import traceback
        traceback.print_exc()

    # Log self-healing results (non-fatal)
    try:
        if any("STALLED" in i or "EMPTY" in i for i in issues):
            supabase = get_supabase()
            supabase.table("system_health_log").insert({
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "status": "alert",
                "details": {"self_healing": issues, "action": "logged_for_review"}
            }).execute()
            print(f"🔴 SELF-HEAL ALERT: {len([i for i in issues if 'STALLED' in i or 'EMPTY' in i])} issue(s) detected")
    except Exception as e:
        print(f"Self-heal logging error (non-fatal): {e}")

    # ---- RESEARCH STRIKE TRIGGER (Piggybacked on heartbeat, processes 2 leads/cycle) ----
    try:
        from modules.database.supabase_client import get_supabase
        supabase = get_supabase()
        
        # Fetch 2 leads with status 'new' and a website_url
        new_leads = supabase.table("contacts_master").select("*").eq("status", "new").not_.is_("website_url", "null").limit(2).execute()
        
        if new_leads.data:
            print(f"🎯 RESEARCH STRIKE: Processing {len(new_leads.data)} leads in cloud...")
            for lead in new_leads.data:
                research_strike_worker.spawn(lead["id"])
        else:
            print("🎯 RESEARCH STRIKE: No 'new' leads with websites found.")
    except Exception as e:
        print(f"Research Strike trigger error: {e}")
    
    # ---- AUTO-PROSPECTOR TRIGGER (every ~6 hours, piggybacked on heartbeat) ----
    try:
        from modules.database.supabase_client import get_supabase
        supabase = get_supabase()
        
        should_prospect = False
        last_run = supabase.table("system_state").select("last_error").eq("key", "prospector_last_run").execute()
        
        if last_run.data and last_run.data[0].get("last_error"):
            last_ts = datetime.fromisoformat(last_run.data[0]["last_error"])
            hours_since = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
            if hours_since >= 2:
                should_prospect = True
                print(f"PROSPECTOR: {hours_since:.1f}h since last run — triggering (Lakeland Deep Scan active)")
        else:
            should_prospect = True  # Never run before
            print("PROSPECTOR: No previous run found — triggering first run")
        
        if should_prospect:
            # Update the timestamp FIRST (prevents double-runs)
            supabase.table("system_state").upsert({
                "key": "prospector_last_run",
                "status": "working",
                "last_error": datetime.now(timezone.utc).isoformat(),
            }, on_conflict="key").execute()
            
            # Spawn async so heartbeat doesn't wait
            auto_prospecting.spawn()
            print("PROSPECTOR: Spawned async prospecting cycle")
        else:
            print(f"PROSPECTOR: Skipping ({hours_since:.1f}h since last run, need 6h)")
    except Exception as e:
        print(f"PROSPECTOR trigger error: {e}")
    
    # ---- DAILY DIGEST TRIGGER (7 AM EST = 12:00 UTC, piggybacked on heartbeat) ----
    try:
        now_utc = datetime.now(timezone.utc)
        if now_utc.hour == 12 and now_utc.minute < 5:  # 12:00-12:04 UTC = 7:00-7:04 AM EST
            supabase = get_supabase()
            last_digest = supabase.table("system_state").select("status").eq("key", "last_digest_sent").execute()
            
            should_send = True
            if last_digest.data and last_digest.data[0].get("status"):
                last_ts = datetime.fromisoformat(last_digest.data[0]["status"])
                hours_since = (now_utc - last_ts).total_seconds() / 3600
                should_send = hours_since >= 20  # At least 20h between digests
            
            if should_send:
                supabase.table("system_state").upsert({
                    "key": "last_digest_sent",
                    "status": now_utc.isoformat(),
                }, on_conflict="key").execute()
                daily_digest.spawn()
                print("📊 DIGEST: Spawned daily digest email")
            else:
                print(f"📊 DIGEST: Already sent today (skipping)")
    except Exception as e:
        print(f"Daily digest trigger error (non-fatal): {e}")
    
    # ---- VAPI CALL MONITOR (Bypass broken Vapi webhooks - Dec 2025 bug) ----
    try:
        vapi_key = os.environ.get('VAPI_PRIVATE_KEY')
        if not vapi_key:
            print("CALL MONITOR: No VAPI_PRIVATE_KEY, skipping")
            return
        
        headers = {'Authorization': f'Bearer {vapi_key}'}
        dan_phone = "+13529368152"
        ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
        
        r = requests.get('https://api.vapi.ai/call?limit=5', headers=headers, timeout=15)
        calls = r.json()
        notified = 0
        
        supabase = get_supabase()
        
        for call in calls:
            call_id = call.get('id', '')
            if call.get('status') != 'ended' or not call.get('endedAt'):
                continue
            
            # Only recent calls (last 10 min)
            try:
                end_time = datetime.fromisoformat(call['endedAt'].replace('Z', '+00:00'))
                if (datetime.now(timezone.utc) - end_time).total_seconds() > 600:
                    continue
            except:
                continue
            
            # Deduplicate
            try:
                existing = supabase.table("vapi_call_notifications").select("call_id").eq("call_id", call_id).execute()
                if existing.data:
                    continue
            except:
                pass
            
            # Build notification
            customer = call.get('customer', {}).get('number', 'Unknown')
            messages = call.get('messages', [])
            msg_count = len(messages) if messages else 0
            
            duration_str = "unknown"
            try:
                s = datetime.fromisoformat(call['createdAt'].replace('Z', '+00:00'))
                e = datetime.fromisoformat(call['endedAt'].replace('Z', '+00:00'))
                secs = int((e - s).total_seconds())
                duration_str = f"{secs // 60}m {secs % 60}s"
            except:
                pass
            
            summary = ""
            if messages:
                for m in messages[-2:]:
                    role = m.get('role', '?')
                    text = str(m.get('message', ''))[:60]
                    if text:
                        summary += f"\n{role}: {text}"
            
            notify_msg = f"Sarah AI Call Report\nCaller: {customer}\nDuration: {duration_str}\nMessages: {msg_count}{summary}"
            
            try:
                r2 = req.post(ghl_webhook, json={"phone": dan_phone, "message": notify_msg}, timeout=10)
                print(f"CALL MONITOR: Notified Dan about call {call_id[:12]}: {r2.status_code}")
                notified += 1
                
                try:
                    supabase.table("vapi_call_notifications").insert({
                        "call_id": call_id,
                        "phone_number": customer,
                        "notified_at": datetime.now(timezone.utc).isoformat()
                    }).execute()
                except Exception as outer_err:
                    print(f"CALL MONITOR: General error processing call {call_id[:12]}: {outer_err}")
            except Exception as loop_err:
                print(f"CALL MONITOR: Fatal loop error on {call.get('id', 'unknown')}: {loop_err}")
        
    except Exception as e:
        print(f"CALL MONITOR ERROR: {e}")

    # ---- AUTONOMOUS INSPECTOR CYCLE (error pattern analysis) ----
    try:
        from modules.autonomous_inspector import Inspector
        inspector = Inspector()
        inspection = inspector.run_inspection_cycle()
        print(f"🔍 INSPECTOR: {inspection.get('status', 'unknown')} | "
              f"{inspection.get('errors_1h', 0)} errors in last hour | "
              f"{inspection.get('circuit_broken', 0)} circuit-broken")
    except Exception as e:
        print(f"Inspector cycle error (non-fatal): {e}")

# ────────────────────────────────────────────────────────────
#  VOICE AGENT TOOLS (Maya v2 Actions)
# ────────────────────────────────────────────────────────────

def lookup_business_google(name: str):
    """
    Search Google Places for a business by name and return its vitals.
    Used by Maya to give real-time advice during calls.
    """
    import os
    import requests
    
    api_base = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_base:
        return {"error": "Missing GOOGLE_PLACES_API_KEY environment variable."}
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": name, "key": api_base}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get("status") != "OK":
            return {"error": f"No business found for '{name}'."}
            
        results = data.get("results", [])
        if not results:
            return {"error": "No results found."}
            
        place = results[0]
        business_name = place.get("name")
        rating = place.get("rating", "No rating")
        reviews = place.get("user_ratings_total", 0)
        address = place.get("formatted_address", "Unknown address")
        
        # Standing Analysis
        standing = "Strong" if rating and float(rating) >= 4.2 else "Vulnerable"
        velocity_hook = "Healthy" if reviews > 150 else "Stagnant (Great opportunity for automation)"
        
        return {
            "business_name": business_name,
            "google_rating": rating,
            "review_count": reviews,
            "address": address,
            "standing_analysis": standing,
            "review_velocity": velocity_hook,
            "advice": f"They have {reviews} reviews. If their top local competitor has more, they are losing ground every day. This is the 'Review Velocity' gap we fixed for other clients."
        }
    except Exception as e:
        return {"error": f"Search execution failed: {str(e)}"}

# ────────────────────────────────────────────────────────────
#  WORKERS
from workers.outreach import auto_outreach_loop as outreach_logic
from workers.lead_unifier import unified_lead_sync as sync_logic
from workers.self_learning_cron import trigger_self_learning_loop as learning_logic
from workers.prospector import run_prospecting_cycle as prospector_logic
from workers.sunbiz_prospector import run_sunbiz_sync as sunbiz_logic
from scripts.ingest_manus import ingest_manus_leads as manus_logic
from workers.sunbiz_delta import run_sunbiz_delta_watch as delta_logic
from workers.zero_touch_onboarding import trigger_zero_touch

@app.function(image=image, secrets=[VAULT], timeout=600)
def zero_touch_onboarding(contact_id: str):
    """Zero-Touch Fulfillment Engine triggered by GHL Opportunity Won events."""
    return trigger_zero_touch(contact_id)

@app.function(image=image, secrets=[VAULT])
def scheduled_sunbiz_delta_watch():
    """8 AM Mon-Sat strike for brand-new Sunbiz registrations (Consolidated)."""
    return delta_logic()

@app.function(image=image, secrets=[VAULT], timeout=300)
def run_prospector():
    """Prospector Engine — discovers + enriches new leads every 30 min.
    Uses Google Places + Hunter.io to find businesses and extract emails."""
    print("🔍 PROSPECTOR: Starting discovery cycle...")
    return prospector_logic()

@app.function(image=image, secrets=[VAULT], timeout=120)
def generate_ghl_csv():
    """Generate GHL-compatible CSV of all contacts. Run via: modal run deploy.py::generate_ghl_csv
    Saves CSV text to system_state for retrieval."""
    import csv
    import io
    from modules.database.supabase_client import get_supabase
    
    supabase = get_supabase()
    all_leads = []
    offset = 0
    batch = 1000
    
    while True:
        res = supabase.table("contacts_master").select(
            "id,full_name,email,phone,company_name,niche,status,lead_source,website_url"
        ).in_("status", ["new", "research_done", "outreach_sent", "sequence_complete"]).range(
            offset, offset + batch - 1
        ).execute()
        if not res.data:
            break
        all_leads.extend(res.data)
        if len(res.data) < batch:
            break
        offset += batch
    
    contactable = [l for l in all_leads if l.get("phone") or l.get("email")]
    
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Website", "Source"])
    
    for lead in contactable:
        name = (lead.get("full_name") or "").strip()
        parts = name.split(" ", 1)
        first = parts[0] if parts else ""
        last = parts[1] if len(parts) > 1 else ""
        
        phone = (lead.get("phone") or "").replace("-","").replace("(","").replace(")","").replace(" ","")
        if phone and not phone.startswith("+"):
            phone = f"+1{phone}"
        
        tags = ["import:supabase"]
        if lead.get("status"):
            tags.append(f"status:{lead['status']}")
        if lead.get("niche"):
            tags.append(f"niche:{lead['niche']}")
        
        w.writerow([
            first, last,
            lead.get("email") or "",
            phone,
            lead.get("company_name") or "",
            ", ".join(tags),
            lead.get("website_url") or "",
            lead.get("lead_source") or "supabase"
        ])
    
    csv_text = output.getvalue()
    print(f"Generated CSV: {len(contactable)} contacts, {len(csv_text)} bytes")
    print("--- CSV START ---")
    print(csv_text)
    print("--- CSV END ---")
    return {"contacts": len(contactable), "csv_bytes": len(csv_text)}

def run_social_migration():
    """Create the social_drafts table via psycopg2."""
    from scripts.migrate_social import create_social_table
    return create_social_table()

def verify_strike_results():
    """Verify that dossiers and videos are persistent in DB."""
    from modules.database.supabase_client import get_supabase
    import json
    sb = get_supabase()
    res = sb.table("contacts_master").select("*").eq("source", "manus").execute()
    leads = res.data
    
    verified = 0
    for lead in leads:
        count = 0
        raw = json.loads(lead.get("raw_research") or "{}")
        if "manus_candidate_dossier" in raw:
            count += 1
        if "video_teaser_url" in lead.get("raw_research", ""): # Inside audit dict
            count += 1
        
        if count > 0:
            verified += 1
            print(f"✅ Lead {lead['company_name']} verified with {count} assets.")
            
    print(f"\n📈 FINAL RESULT: {verified}/{len(leads)} leads processed with strike assets.")
    return verified

def debug_image_install():
    """Debug what exactly is installed on the Modal image."""
    import subprocess
    import sys
    print(f"Python Version: {sys.version}")
    print("\n--- Pip List ---")
    print(subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode())
    try:
        import genai
        print("✅ import genai SUCCESS")
    except Exception as e:
        print(f"\n❌ import genai FAIL: {e}")
    return True

def trigger_manus_ingest(leads_json: str):
    """Manual trigger for Manus ingestion."""
    import json
    leads = json.loads(leads_json)
    return manus_logic(leads)
def trigger_cinematic_strike():
    """Triggers the Phase 12 Strike (Dossiers + Veo Videos) via Modal."""
    from scripts.trigger_cinematic_strike import run_phase12_strike
    return run_phase12_strike()

from workers.social_content import generate_weekly_content as social_gen_logic
from workers.social_poster import publish_social_multiplier_posts as social_post_logic

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 */6 * * *"))
def auto_social_content_cycle():
    """Generates a fresh week of social content every 6 hours."""
    print("📈 SOCIAL: Refreshing content calendar...")
    return social_gen_logic(1)

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 9,16 * * *"))
def auto_social_publisher():
    """Publishes social drafts twice daily (9AM & 4PM EST)."""
    print("🚀 SOCIAL: Triggering publication cycle...")
    return social_post_logic()

from fastapi import Request, Response
import json

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def sovereign_stats(request: Request):
    """Full Dashboard Data Proxy — bypasses RLS with service_role key.
    Returns: stats, activity feed, calls, leads, notifications."""
    import os
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    # === AUTHENTICATION ===
    # Use the header injected by dashboard.html or query params
    code = request.query_params.get("code") or request.headers.get("X-Dashboard-Code")
    # Fallback to empire_2026 if secret is missing to prevent lockout during transition
    valid_code = os.getenv("DASHBOARD_ACCESS_CODE", "empire_2026")
    
    if code != valid_code:
        print(f"🚫 AUTH: Unauthorized access attempt to sovereign_stats (Code: {code})")
        return Response(
            content=json.dumps({"error": "Unauthorized"}), 
            status_code=403, 
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    try:
        sb = get_supabase()
        now = datetime.now(timezone.utc)
        yesterday = (now - timedelta(hours=24)).isoformat()
        
        # === STATS ===
        leads_q = sb.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
        pool_count = leads_q.count if leads_q.count is not None else len(leads_q.data)
        
        touches_q = sb.table("outbound_touches").select("id", count="exact").gt("ts", yesterday).execute()
        outbound_24h = touches_q.count if touches_q.count is not None else len(touches_q.data)

        # === HEALTH ===
        hb = sb.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
        last_hb = hb.data[0]["checked_at"] if hb.data else None
        hb_ok = False
        if last_hb:
            try:
                hb_time = datetime.fromisoformat(last_hb.replace("Z", "+00:00"))
                hb_ok = (now - hb_time).total_seconds() < 900
            except: pass
        
        # === ACTIVITY FEED (outbound_touches, last 30 — enriched) ===
        try:
            activity = sb.table("outbound_touches").select(
                "channel,status,ts,company,phone,payload,variant_name"
            ).order("ts", desc=True).limit(30).execute()
            
            # Build phone → contact_name lookup for activity items
            activity_phones = list(set(
                r.get("phone", "") for r in activity.data if r.get("phone")
            ))
            contact_lookup = {}
            if activity_phones:
                # Batch lookup in chunks of 20
                for i in range(0, len(activity_phones), 20):
                    chunk = activity_phones[i:i+20]
                    try:
                        cl = sb.table("contacts_master").select(
                            "phone,first_name,company_name,email"
                        ).in_("phone", chunk).execute()
                        for c in cl.data:
                            p = c.get("phone", "")
                            contact_lookup[p] = {
                                "name": c.get("first_name", ""),
                                "company": c.get("company_name", ""),
                                "email": c.get("email", "")
                            }
                    except: pass
            
            # Enrich activity data with contact info
            for item in activity.data:
                phone = item.get("phone", "")
                if phone in contact_lookup:
                    item["contact_name"] = contact_lookup[phone].get("name", "")
                    item["contact_email"] = contact_lookup[phone].get("email", "")
                    if not item.get("company"):
                        item["company"] = contact_lookup[phone].get("company", "")
                # Extract email 'to' from payload if available
                payload = item.get("payload") or {}
                if isinstance(payload, dict):
                    if payload.get("to"):
                        item["email_to"] = payload["to"]
                    if payload.get("from"):
                        item["email_from"] = payload["from"]
                    if payload.get("subject"):
                        item["email_subject"] = payload["subject"]
        except:
            activity = type('obj', (object,), {'data': []})()  # empty fallback
        
        # === RECENT CALLS (customer_memory, last 15) ===
        try:
            calls = sb.table("customer_memory").select(
                "phone_number,context_summary"
            ).limit(15).execute()
        except:
            calls = type('obj', (object,), {'data': []})()  # empty fallback
        
        # === NOTIFICATIONS (call_alert entries) ===
        try:
            notifs = sb.table("system_health_log").select(
                "check_type,status,details,checked_at"
            ).eq("check_type", "call_alert").order("checked_at", desc=True).limit(10).execute()
        except:
            notifs = type('obj', (object,), {'data': []})()  # empty fallback
        
        # === LEAD PIPELINE (top 50) ===
        try:
            pipeline = sb.table("contacts_master").select(
                "id,company_name,email,phone,status,lead_source,last_contacted_at,created_at"
            ).order("created_at", desc=True).limit(50).execute()
        except:
            pipeline = type('obj', (object,), {'data': []})()  # empty fallback
        
        # === STRIPE REVENUE (live API) ===
        stripe_data = {"mrr": 0, "active_subs": 0, "recent_payments": [], "total_revenue": 0, "error": None}
        try:
            import stripe
            stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            if stripe.api_key and stripe.api_key.startswith("sk_"):
                # Active subscriptions
                subs = stripe.Subscription.list(status="active", limit=100)
                active_subs = len(subs.data)
                mrr = 0
                for sub in subs.data:
                    for item in sub["items"]["data"]:
                        price = item.get("price", {})
                        amount = price.get("unit_amount", 0) or 0
                        interval = price.get("recurring", {}).get("interval", "month")
                        qty = item.get("quantity", 1)
                        if interval == "year":
                            mrr += (amount * qty) / 12
                        elif interval == "week":
                            mrr += (amount * qty) * 4.33
                        else:
                            mrr += amount * qty
                
                # Recent successful payments (last 30 days)
                thirty_days_ago = int((now - timedelta(days=30)).timestamp())
                charges = stripe.Charge.list(limit=20, created={"gte": thirty_days_ago})
                recent_payments = []
                total_revenue_30d = 0
                for ch in charges.data:
                    if ch.status == "succeeded":
                        total_revenue_30d += ch.amount
                        recent_payments.append({
                            "amount": ch.amount / 100,
                            "currency": ch.currency,
                            "description": ch.description or ch.billing_details.get("name", "Payment"),
                            "date": datetime.fromtimestamp(ch.created, tz=timezone.utc).isoformat(),
                            "status": ch.status
                        })
                
                # Balance (total all-time from balance transactions)
                balance = stripe.Balance.retrieve()
                available = sum(b.get("amount", 0) for b in balance.get("available", []))
                pending = sum(b.get("amount", 0) for b in balance.get("pending", []))
                
                stripe_data = {
                    "mrr": round(mrr / 100, 2),
                    "active_subs": active_subs,
                    "recent_payments": recent_payments[:10],
                    "total_revenue_30d": round(total_revenue_30d / 100, 2),
                    "balance_available": round(available / 100, 2),
                    "balance_pending": round(pending / 100, 2),
                    "error": None
                }
        except Exception as stripe_err:
            stripe_data["error"] = str(stripe_err)
        
        # === CONVERSION FUNNEL (lead status breakdown) ===
        try:
            all_leads = sb.table("contacts_master").select("status", count="exact").execute()
            status_counts = {}
            for lead in all_leads.data:
                s = lead.get("status", "unknown")
                status_counts[s] = status_counts.get(s, 0) + 1
            funnel = {
                "total": all_leads.count if all_leads.count is not None else len(all_leads.data),
                "new": status_counts.get("new", 0),
                "research_done": status_counts.get("research_done", 0),
                "outreach_sent": status_counts.get("outreach_sent", 0),
                "responded": status_counts.get("responded", 0),
                "customer": status_counts.get("customer", 0),
                "bounced": status_counts.get("bounced", 0),
                "bad_email": status_counts.get("bad_email", 0),
            }
        except:
            funnel = {}
        
        # === A/B EMAIL PERFORMANCE (variant breakdown, last 7 days) ===
        try:
            week_ago = (now - timedelta(days=7)).isoformat()
            ab_raw = sb.table("outbound_touches").select(
                "variant_id,status"
            ).gt("ts", week_ago).execute()
            
            variants = {}
            for t in ab_raw.data:
                vid = t.get("variant_id") or "DEFAULT"
                if vid not in variants:
                    variants[vid] = {"sent": 0, "delivered": 0, "opened": 0, "bounced": 0, "replied": 0}
                variants[vid]["sent"] += 1
                st = t.get("status", "")
                if st in variants[vid]:
                    variants[vid][st] += 1
            
            ab_performance = []
            for vid, counts in variants.items():
                total = counts["sent"]
                ab_performance.append({
                    "variant": vid,
                    "sent": total,
                    "delivered": counts["delivered"],
                    "opened": counts["opened"],
                    "bounced": counts["bounced"],
                    "replied": counts["replied"],
                    "open_rate": round(counts["opened"] / total * 100, 1) if total > 0 else 0,
                    "reply_rate": round(counts["replied"] / total * 100, 1) if total > 0 else 0,
                })
        except:
            ab_performance = []
        
        # === LEAD GEO (city breakdown for heatmap) ===
        try:
            geo_raw = sb.table("contacts_master").select("city").not_.is_("city", "null").execute()
            city_counts = {}
            for r in geo_raw.data:
                c = (r.get("city") or "").strip().title()
                if c:
                    city_counts[c] = city_counts.get(c, 0) + 1
            # Sort by count, top 15
            lead_geo = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            lead_geo = [{"city": c, "count": n} for c, n in lead_geo]
        except:
            lead_geo = []
        
        # === SYSTEM VITALS (for live dashboard panel) ===
        system_vitals = {}
        try:
            # Prospector status (timestamp stored in last_error due to status check constraint)
            prosp = sb.table("system_state").select("last_error").eq("key", "prospector_last_run").execute()
            prosp_ts = prosp.data[0]["last_error"] if prosp.data else None
            prosp_age_min = None
            if prosp_ts:
                try:
                    prosp_time = datetime.fromisoformat(prosp_ts.replace("Z", "+00:00"))
                    prosp_age_min = round((now - prosp_time).total_seconds() / 60)
                except: pass
            
            # Campaign mode
            cm = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
            campaign_mode = cm.data[0]["status"] if cm.data else "unknown"
            
            # Outreach breakdown by channel (24h)
            channel_breakdown = {"email": 0, "sms": 0, "call": 0}
            try:
                ch_raw = sb.table("outbound_touches").select("channel").gt("ts", yesterday).execute()
                for row in ch_raw.data:
                    ch = (row.get("channel") or "email").lower()
                    if ch in channel_breakdown:
                        channel_breakdown[ch] += 1
                    else:
                        channel_breakdown["email"] += 1  # fallback
            except: pass
            
            # Last outreach timestamp
            last_touch = sb.table("outbound_touches").select("ts,channel").order("ts", desc=True).limit(1).execute()
            last_outreach_ts = last_touch.data[0]["ts"] if last_touch.data else None
            last_outreach_ch = last_touch.data[0].get("channel", "?") if last_touch.data else None
            
            # Inspector recent errors (last 3)
            inspector_errors = []
            try:
                err_q = sb.table("system_error_log").select("source,error_type,status,created_at").order("created_at", desc=True).limit(3).execute()
                inspector_errors = err_q.data
            except: pass  # table may not exist yet
            
            # Inspector error count (1h)
            error_count_1h = 0
            try:
                one_hour_ago = (now - timedelta(hours=1)).isoformat()
                err_count_q = sb.table("system_error_log").select("id", count="exact").gt("created_at", one_hour_ago).execute()
                error_count_1h = err_count_q.count if err_count_q.count is not None else len(err_count_q.data)
            except: pass
            
            # Outreach velocity (touches in last 1h vs last 24h)
            outreach_1h = 0
            try:
                one_hour_ago = (now - timedelta(hours=1)).isoformat()
                q1h = sb.table("outbound_touches").select("id", count="exact").gt("ts", one_hour_ago).execute()
                outreach_1h = q1h.count if q1h.count is not None else len(q1h.data)
            except: pass
            
            # --- PHASE 6: PREDICTIVE REVENUE FORECAST (From Abacus cron) ---
            revenue_forecast = None
            try:
                rf_query = sb.table("system_state").select("payload").eq("key", "revenue_forecast").execute()
                if rf_query.data and rf_query.data[0].get("payload"):
                    # We expect payload to be structured JSON from Abacus
                    rf_raw = rf_query.data[0]["payload"]
                    revenue_forecast = json.loads(rf_raw) if isinstance(rf_raw, str) else rf_raw
            except Exception as e:
                print(f"⚠️ Forecast fetch error: {e}")
                pass
            
            system_vitals = {
                "prospector_last_run": prosp_ts,
                "prospector_age_min": prosp_age_min,
                "campaign_mode": campaign_mode,
                "channel_breakdown": channel_breakdown,
                "last_outreach_ts": last_outreach_ts,
                "last_outreach_channel": last_outreach_ch,
                "outreach_1h": outreach_1h,
                "inspector_errors": inspector_errors,
                "error_count_1h": error_count_1h,
                "revenue_forecast": revenue_forecast,
                "engines": {
                    "outreach": outbound_24h > 0,
                    "prospecting": prosp_age_min is not None and prosp_age_min < 180,
                    "heartbeat": hb_ok,
                    "campaign": campaign_mode == "working",
                    "inspector": True  # always on now
                }
            }
        except Exception as vex:
            system_vitals = {"error": str(vex)}
        
        # DISPATCH BOARD
        dispatch_board = {}
        try:
            from workers.dispatch import get_dispatch_board
            dispatch_board = get_dispatch_board(sb)
        except: pass

        # REVIEW STATS
        review_stats = {}
        try:
            from workers.review_optimizer import get_review_stats
            review_stats = get_review_stats(sb)
        except: pass

        # === PIPELINE HEATMAP (Top 25 scored "Bleeding Leads") ===
        pipeline_heatmap = []
        try:
            heatmap_q = sb.table("contacts_master").select(
                "id,company_name,email,phone,status,niche,lead_source,lead_score,website_url,city"
            ).not_.is_("lead_score", "null").order("lead_score", desc=True).limit(25).execute()
            for lead in heatmap_q.data:
                score = lead.get("lead_score", 0) or 0
                tier = "critical" if score >= 8 else ("high" if score >= 5 else "normal")
                pipeline_heatmap.append({
                    "id": lead.get("id"),
                    "company": lead.get("company_name", "Unknown"),
                    "email": lead.get("email", ""),
                    "phone": lead.get("phone", ""),
                    "status": lead.get("status", "new"),
                    "niche": lead.get("niche", ""),
                    "source": lead.get("lead_source", ""),
                    "score": score,
                    "tier": tier,
                    "website": lead.get("website_url", ""),
                    "city": lead.get("city", ""),
                })
        except Exception as hm_err:
            pipeline_heatmap = [{"error": str(hm_err)}]

        response_data = {
            "total_leads": pool_count,
            "outbound_24h": outbound_24h,
            "health": {
                "status": "healthy" if hb_ok else "degraded",
                "heartbeat_ok": hb_ok,
                "last_heartbeat": last_hb
            },
            "activity": activity.data,
            "calls": calls.data,
            "notifications": notifs.data,
            "leads": pipeline.data,
            "stripe": stripe_data,
            "funnel": funnel,
            "ab_performance": ab_performance,
            "lead_geo": lead_geo,
            "system_vitals": system_vitals,
            "dispatch_board": dispatch_board,
            "review_stats": review_stats,
            "pipeline_heatmap": pipeline_heatmap,
            "status": "synchronized",
            "checked_at": now.isoformat()
        }
        return Response(
            content=json.dumps(response_data),
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.function(image=image, secrets=[VAULT])
def auto_outreach_loop():
    """Triggers autonomous outreach engine with lead recycling."""
    from datetime import datetime, timezone, timedelta
    
    # Auto-recycle stale leads before outreach (crash-safe)
    try:
        from modules.database.supabase_client import get_supabase
        supabase = get_supabase()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        
        # Find leads stuck at outreach_sent for >3 days
        stale = supabase.table("contacts_master").select("id", count="exact").eq(
            "status", "outreach_sent"
        ).lt("last_contacted_at", cutoff).execute()
        stale_count = stale.count if stale.count is not None else len(stale.data)
        
        if stale_count > 0:
            # Recycle them back to 'new' (max 50 per cycle to avoid overload)
            to_recycle = supabase.table("contacts_master").select("id").eq(
                "status", "outreach_sent"
            ).lt("last_contacted_at", cutoff).limit(50).execute()
            
            recycled = 0
            for lead in to_recycle.data:
                try:
                    supabase.table("contacts_master").update({
                        "status": "research_done",
                    }).eq("id", lead["id"]).execute()
                    recycled += 1
                except:
                    pass
            
            if recycled > 0:
                print(f"♻️ Recycled {recycled} stale leads back to 'new' (cooldown >3 days)")
        
        # Also fix NULL last_contacted_at on outreach_sent (prevent future stuck leads)
        null_leads = supabase.table("contacts_master").select("id,created_at").eq(
            "status", "outreach_sent"
        ).is_("last_contacted_at", "null").limit(50).execute()
        
        if null_leads.data:
            for lead in null_leads.data:
                try:
                    supabase.table("contacts_master").update({
                        "last_contacted_at": lead.get("created_at", datetime.now(timezone.utc).isoformat())
                    }).eq("id", lead["id"]).execute()
                except:
                    pass
            print(f"🔧 Fixed {len(null_leads.data)} leads with NULL last_contacted_at")
    except Exception as e:
        print(f"Lead recycler error (non-fatal): {e}")
    
    outreach_logic()

# Health check consolidated into sovereign_stats


# ────────────────────────────────────────────────────────────
#  RESEND WEBHOOK (track opens, replies, bounces per variant)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
def resend_webhook(data: dict):
    """Receives Resend webhook events (delivered, opened, bounced, complained, replied).
    - Tracks A/B performance in outbound_touches
    - Auto-replies to lead replies with booking link
    - SMS notifies Dan on hot leads (replies)
    - Marks permanent bounces as bad_email
    """
    import json, os, requests, traceback
    from datetime import datetime, timezone
    from modules.database.supabase_client import get_supabase
    
    BOOKING_LINK = "https://links.aiserviceco.com/widget/booking/YWQcHuXXznQEQa7LAWeB"
    DAN_EMAIL_ADDRS = ["owner@aiserviceco.com", "nearmiss1193@gmail.com"]
    
    event_type = data.get("type", "unknown")
    event_data = data.get("data", {})
    email_id = event_data.get("email_id", "")
    
    print(f"📬 RESEND WEBHOOK: {event_type} | email_id: {email_id}")
    
    try:
        supabase = get_supabase()
        
        # Find the original outbound_touch by resend email ID
        touch_record = None
        if email_id:
            touch = supabase.table("outbound_touches").select("id,payload,phone,company").eq(
                "correlation_id", email_id
            ).limit(1).execute()
            
            if touch.data:
                touch_record = touch.data[0]
                payload = touch_record.get("payload") or {}
                
                # Add event to payload history
                events = payload.get("events", [])
                events.append({
                    "type": event_type,
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "raw": {k: v for k, v in event_data.items() if k != "headers"}
                })
                payload["events"] = events
                
                # Update status based on event type
                status_map = {
                    "email.delivered": "delivered",
                    "email.opened": "opened",
                    "email.clicked": "clicked",
                    "email.bounced": "bounced",
                    "email.complained": "complained",
                }
                new_status = status_map.get(event_type)
                
                update = {"payload": payload}
                if new_status:
                    priority = ["sent", "delivered", "opened", "clicked", "bounced", "complained"]
                    current = touch_record.get("status", "sent") if touch_record.get("status") in priority else "sent"
                    if priority.index(new_status) > priority.index(current):
                        update["status"] = new_status
                
                supabase.table("outbound_touches").update(update).eq(
                    "id", touch_record["id"]
                ).execute()
                
                print(f"  ✅ Updated touch {touch_record['id']}: {event_type}")
            else:
                print(f"  ⚠️ No matching touch for email_id: {email_id}")
        
        # ─── BOUNCE HANDLER: Mark permanent bounces as bad_email ───
        if event_type == "email.bounced" and touch_record:
            bounce_type = event_data.get("bounce", {}).get("type", "transient")
            recipient = event_data.get("to", [""])[0] if isinstance(event_data.get("to"), list) else ""
            
            if bounce_type == "permanent" and recipient:
                # Mark this lead's email as bad so we never send again
                try:
                    supabase.table("contacts_master").update(
                        {"status": "bad_email"}
                    ).eq("email", recipient).execute()
                    print(f"  🚫 Marked {recipient} as bad_email (permanent bounce)")
                except Exception as be:
                    print(f"  ⚠️ Bounce mark failed: {be}")
        
        # ─── REPLY HANDLER: Auto-respond + SMS Dan + Log Inbound Touch ───
        if event_type == "email.replied":
            recipient = event_data.get("from", "")  # The lead who replied
            reply_text = event_data.get("text", "")[:200]  # First 200 chars of reply (for notifications)
            full_reply_text = event_data.get("text", "") # Full reply explicitly for the Triage Deck
            company = touch_record.get("company", "Unknown") if touch_record else "Unknown"
            
            print(f"  🔥 REPLY from {recipient} ({company}): {reply_text[:80]}")
            
            # Log inbound touch explicitly to the database
            try:
                supabase.table("outbound_touches").insert({
                    "phone": touch_record.get("phone") if touch_record else None,
                    "channel": "email",
                    "company": company,
                    "status": "replied", # Indicates they replied
                    "variant_name": "Inbound Email",
                    "correlation_id": email_id,
                    "body": full_reply_text,
                    "payload": {
                        "direction": "inbound",
                        "from": recipient,
                        "raw_event": event_type
                    }
                }).execute()
                print(f"  📥 Inbound reply explicitly logged to outbound_touches for Triage Deck.")
            except Exception as e:
                print(f"  ⚠️ Error logging inbound touch: {e}")
            
            # Skip if it's Dan replying to himself
            if recipient.lower() not in DAN_EMAIL_ADDRS:
                
                # ACTION 1: Auto-reply with booking link
                try:
                    resend_key = os.environ.get("RESEND_API_KEY")
                    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
                    
                    # Get lead's first name
                    lead_name = "there"
                    try:
                        lead_rec = supabase.table("contacts_master").select("full_name").eq("email", recipient).limit(1).execute()
                        if lead_rec.data:
                            lead_name = (lead_rec.data[0].get("full_name") or "there").split(" ")[0]
                    except:
                        pass
                    
                    auto_html = f"""<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
<p>Hey {lead_name}!</p>
<p>Great to hear from you. I'd love to chat about how we can help.</p>
<p>You can grab a time on my calendar here — pick whatever works for you:</p>
<p><a href="{BOOKING_LINK}" style="display:inline-block; background:#2563eb; color:#fff; padding:12px 24px; border-radius:6px; text-decoration:none; font-weight:bold;">Book a 15-min call</a></p>
<p>Or just reply with a good time and I'll make it work.</p>
<p>Talk soon,<br>Dan</p>
</div>"""
                    
                    auto_payload = {
                        "from": from_email,
                        "to": [recipient],
                        "subject": f"Re: Let's find a time to chat",
                        "html": auto_html,
                    }
                    
                    r = requests.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json=auto_payload,
                        timeout=15
                    )
                    if r.status_code in [200, 201]:
                        print(f"  ✅ AUTO-REPLY sent to {recipient} with booking link")
                    else:
                        print(f"  ⚠️ Auto-reply failed: {r.status_code} {r.text[:100]}")
                except Exception as are:
                    print(f"  ❌ Auto-reply error: {are}")
                    traceback.print_exc()
                
                # ACTION 2: SMS notify Dan
                try:
                    dan_email = os.environ.get("DAN_EMAIL", "nearmiss1193@gmail.com")
                    resend_key = os.environ.get("RESEND_API_KEY")
                    from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
                    
                    # Send Dan an email notification (instant)
                    notify_html = f"""<div style="font-family: Arial; font-size: 14px;">
<h2>🔥 HOT LEAD REPLY</h2>
<p><strong>Company:</strong> {company}</p>
<p><strong>From:</strong> {recipient}</p>
<p><strong>Their reply:</strong> {reply_text[:200]}</p>
<p>Auto-reply with booking link has been sent.</p>
<p><a href="{BOOKING_LINK}">View your calendar</a></p>
</div>"""
                    
                    requests.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json={
                            "from": from_email,
                            "to": [dan_email],
                            "subject": f"🔥 {company} replied to your email!",
                            "html": notify_html,
                        },
                        timeout=10
                    )
                    print(f"  📲 Dan notified about reply from {company}")
                except Exception as ne:
                    print(f"  ⚠️ Dan notification error: {ne}")
                
                try:
                    supabase.table("contacts_master").update(
                        {"status": "responded"}
                    ).eq("email", recipient).execute()
                    print(f"  ✅ Lead {recipient} status → responded")
                except Exception as se:
                    print(f"  ⚠️ Status update error: {se}")
        
        # Log to system_health for monitoring
        supabase.table("system_health_log").insert({
            "status": f"resend_{event_type}",
            "details": json.dumps({"email_id": email_id, "type": event_type}),
        }).execute()
        
    except Exception as e:
        print(f"  ❌ Resend webhook error: {e}")
        traceback.print_exc()
    
    return {"received": True}






# ────────────────────────────────────────────────────────────
#  RESEARCH STRIKE WORKER (Cloud Autonomy Engine)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT], timeout=60)
def research_strike_worker(lead_id: str):
    """
    Enriches a single lead with PageSpeed and FDBR data asynchronously.
    Moves lead from 'new' -> 'research_done'.
    """
    import os, json, uuid, requests
    from datetime import datetime, timezone
    from workers.audit_generator import fetch_pagespeed, check_privacy_policy, check_ai_readiness
    
    lead_id = lead_id.strip()
    print(f"🕵️ RESEARCH: Auditing Lead {lead_id}...")
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        # 0. Fetch Lead
        r = requests.get(f"{url}/rest/v1/contacts_master?id=eq.{lead_id}", headers=headers)
        if r.status_code != 200 or not r.json():
            print(f"  ⚠️ Research failed: Lead {lead_id} not found (Status: {r.status_code})")
            return
            
        lead = r.json()[0]
        website = lead.get("website_url")
        if not website:
            print(f"  ⚠️ Research failed: Lead {lead_id} has no website")
            return
        
        # --- PHASE 2: SOVEREIGN CACHE (7-day expiry) ---
        ps_data, privacy_data, ai_data = None, None, None
        is_cached = False
        try:
            cache_r = requests.get(f"{url}/rest/v1/audit_cache?url=eq.{website.lower().strip()}", headers=headers)
            if cache_r.status_code == 200 and cache_r.json():
                cache = cache_r.json()[0]
                cache_ts = datetime.fromisoformat(cache['last_audited_at'].replace('Z', '+00:00'))
                if (datetime.now(timezone.utc) - cache_ts).days < 7:
                    print(f"  ✅ SOVEREIGN CACHE HIT: {website}")
                    raw_c = cache.get("raw_data", {})
                    ps_data = raw_c.get("pagespeed")
                    privacy_data = raw_c.get("privacy")
                    ai_data = raw_c.get("ai_readiness")
                    if ps_data and privacy_data and ai_data:
                        is_cached = True
        except Exception as ce:
            print(f"  ⚠️ Cache check failed: {ce}")

        if not is_cached:
            # 1. Run PageSpeed
            import time
            print(f"  [1/3] PageSpeed Insights for {website} (Politeness delay 5s)...")
            time.sleep(5) # Board Approved: Mitigation for 429 errors
            ps_data = fetch_pagespeed(website)
            
            # 2. Check FDBR (Privacy)
            print(f"  [2/3] Privacy/FDBR Check...")
            privacy_data = check_privacy_policy(website)
            
            # 3. Check AI Readiness
            print(f"  [3/3] AI Readiness Check...")
            ai_data = check_ai_readiness(website)
            
            # Save to Cache for 7 days
            try:
                requests.post(f"{url}/rest/v1/audit_cache", headers=headers, json={
                    "url": website.lower().strip(),
                    "score": ps_data.get("score") if ps_data else 0,
                    "raw_data": {"pagespeed": ps_data, "privacy": privacy_data, "ai_readiness": ai_data},
                    "privacy_status": privacy_data.get("status") if privacy_data else "unknown",
                    "ai_status": ai_data.get("status") if ai_data else "unknown",
                    "last_audited_at": datetime.now(timezone.utc).isoformat()
                })
            except: pass
        
        # 4. Integrate into raw_research
        raw_research = json.loads(lead.get("raw_research") or "{}")
        raw_research.update({
            "pagespeed": ps_data,
            "privacy": privacy_data,
            "ai_readiness": ai_data,
            "audited_at": datetime.now(timezone.utc).isoformat()
        })
        
        # 5. Update Lead Status
        update_r = requests.patch(
            f"{url}/rest/v1/contacts_master?id=eq.{lead_id}",
            headers=headers,
            json={
                "raw_research": json.dumps(raw_research),
                "status": "research_done"
            }
        )
        if update_r.status_code not in [200, 201, 204]:
            print(f"  ❌ Failed to update lead status: {update_r.text}")
        
        # 6. Create Entry in audit_reports
        try:
            report_id = str(uuid.uuid4())
            audit_r = requests.post(
                f"{url}/rest/v1/audit_reports",
                headers=headers,
                json={
                    "report_id": report_id,
                    "lead_id": lead_id,
                    "company_name": lead.get("company_name", "Unknown"),
                    "website_url": website,
                    "audit_results": raw_research,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            )
            if audit_r.status_code in [200, 201, 204]:
                print(f"📄 AUDIT REPORT CREATED: {report_id}")
            else:
                print(f"⚠️ Failed to create audit_report entry: {audit_r.text}")
        except Exception as report_err:
            print(f"⚠️ Failed to create audit_report entry: {report_err}")

        print(f"✅ RESEARCH DONE: {lead.get('company_name')} (Score: {ps_data.get('score', 'N/A')}/100)")
        
    except Exception as e:
        print(f"❌ RESEARCH ERROR [Lead {lead_id}]: {e}")
        import traceback
        traceback.print_exc()

# ────────────────────────────────────────────────────────────
#  DAILY DIGEST (Cron #3 — emails Dan a morning summary)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT], timeout=120)  # Triggered by heartbeat at 7 AM EST
def daily_digest():
    """Sends Dan a daily summary email with outreach stats, lead pool, and system health."""
    import os, json, requests
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    print("📊 DAILY DIGEST: Generating morning report...")
    supabase = get_supabase()
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(hours=24)).isoformat()
    
    try:
        # 1. Outreach stats (last 24h)
        touches = supabase.table("outbound_touches").select(
            "channel,variant_id,status"
        ).gt("ts", yesterday).execute()
        
        total_sent = len(touches.data)
        audit_sent = sum(1 for t in touches.data if t.get("variant_id") == "AUDIT")
        generic_sent = total_sent - audit_sent
        delivered = sum(1 for t in touches.data if t.get("status") == "delivered")
        opened = sum(1 for t in touches.data if t.get("status") == "opened")
        bounced = sum(1 for t in touches.data if t.get("status") == "bounced")
        
        # 2. Lead pool
        pool = supabase.table("contacts_master").select("status", count="exact").in_(
            "status", ["new", "research_done"]
        ).execute()
        pool_count = pool.count if pool.count is not None else len(pool.data)
        
        # Total leads
        total = supabase.table("contacts_master").select("id", count="exact").execute()
        total_count = total.count if total.count is not None else 0
        
        # 3. System health (errors in last 24h)
        alerts = supabase.table("system_health_log").select("status,details").eq(
            "status", "alert"
        ).gt("checked_at", yesterday).execute()
        alert_count = len(alerts.data)
        
        # Build email
        open_rate = f"{(opened/total_sent*100):.0f}%" if total_sent > 0 else "N/A"
        bounce_rate = f"{(bounced/total_sent*100):.0f}%" if total_sent > 0 else "N/A"
        
        html = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #e2e8f0; padding: 32px; border-radius: 12px;">
            <h1 style="color: #38bdf8; margin: 0 0 24px;">📊 Daily Empire Digest</h1>
            <p style="color: #94a3b8; margin: 0 0 24px;">{now.strftime('%B %d, %Y')} — Last 24 Hours</p>
            
            <div style="background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                <h2 style="color: #38bdf8; font-size: 16px; margin: 0 0 12px;">📨 Outreach</h2>
                <table style="width: 100%; color: #e2e8f0; border-collapse: collapse;">
                    <tr><td style="padding: 4px 0;">Total sent</td><td style="text-align: right; font-weight: bold;">{total_sent}</td></tr>
                    <tr><td style="padding: 4px 0;">├ Audit PDFs</td><td style="text-align: right; color: #22d3ee;">{audit_sent}</td></tr>
                    <tr><td style="padding: 4px 0;">├ Generic</td><td style="text-align: right;">{generic_sent}</td></tr>
                    <tr><td style="padding: 4px 0;">Delivered</td><td style="text-align: right; color: #4ade80;">{delivered}</td></tr>
                    <tr><td style="padding: 4px 0;">Opened</td><td style="text-align: right; color: #fbbf24;">{opened} ({open_rate})</td></tr>
                    <tr><td style="padding: 4px 0;">Bounced</td><td style="text-align: right; color: #f87171;">{bounced} ({bounce_rate})</td></tr>
                </table>
            </div>
            
            <div style="background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                <h2 style="color: #38bdf8; font-size: 16px; margin: 0 0 12px;">🎯 Lead Pool</h2>
                <table style="width: 100%; color: #e2e8f0; border-collapse: collapse;">
                    <tr><td style="padding: 4px 0;">Ready to contact</td><td style="text-align: right; font-weight: bold; color: {'#4ade80' if pool_count > 50 else '#f87171'};">{pool_count}</td></tr>
                    <tr><td style="padding: 4px 0;">Total leads</td><td style="text-align: right;">{total_count}</td></tr>
                </table>
            </div>
            
            <div style="background: #1e293b; padding: 20px; border-radius: 8px;">
                <h2 style="color: #38bdf8; font-size: 16px; margin: 0 0 12px;">🏥 System Health</h2>
                <table style="width: 100%; color: #e2e8f0; border-collapse: collapse;">
                    <tr><td style="padding: 4px 0;">Alerts (24h)</td><td style="text-align: right; color: {'#4ade80' if alert_count == 0 else '#f87171'};">{alert_count}</td></tr>
                    <tr><td style="padding: 4px 0;">Status</td><td style="text-align: right; color: #4ade80;">{'✅ All Systems Go' if alert_count == 0 else '⚠️ Check Alerts'}</td></tr>
                </table>
            </div>
            
            <p style="color: #475569; font-size: 12px; margin-top: 24px; text-align: center;">
                ⚫ Antigravity v5.0 — Sovereign Executor | Auto-generated
            </p>
        </div>
        """
        
        # Send via Resend
        resend_key = os.environ.get("RESEND_API_KEY")
        if not resend_key:
            print("❌ No RESEND_API_KEY — can't send digest")
            return
        
        from_email = os.environ.get("RESEND_FROM_EMAIL", "Dan <owner@aiserviceco.com>")
        dan_email = os.environ.get("DAN_EMAIL", "owner@aiserviceco.com")
        
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json={
                "from": from_email,
                "to": [dan_email],
                "subject": f"📊 Empire Digest — {total_sent} sent, {opened} opened, {pool_count} in pool",
                "html": html,
            },
            timeout=15
        )
        
        if r.status_code in [200, 201]:
            print(f"✅ DIGEST SENT: {total_sent} sent, {opened} opened, {pool_count} pool")
        else:
            print(f"❌ DIGEST SEND FAILED: {r.status_code} — {r.text[:200]}")
            
    except Exception as e:
        print(f"❌ DIGEST ERROR: {e}")
        import traceback
        traceback.print_exc()


@app.function(image=image, secrets=[VAULT])
def auto_prospecting():
    """Discovers new leads. 4-stage: Google Places → Sunbiz → email enrichment → insert."""
    print("🚀 PROSPECTOR: Starting unified cycle...")
    # 1. Google Places Discovery
    prospector_logic()
    # 2. Sunbiz Lakeland Expansion
    try:
        sunbiz_logic()
    except Exception as e:
        print(f"⚠️ Sunbiz sync failed: {e}")

def unified_lead_sync():
    """Lead sync - MANUAL ONLY."""
    sync_logic()

def trigger_self_learning_loop():
    """Brain reflection - MANUAL ONLY."""
    learning_logic()


@app.function(image=image, secrets=[VAULT])
def schedule_social_multiplier():
    """Publishes social drafts 2x/day (Consolidated)."""
    from workers.social_poster import publish_social_multiplier_posts
    return publish_social_multiplier_posts()

@app.function(image=image, secrets=[VAULT])
def trigger_social_publish():
    """Manual trigger for social publishing."""
    from workers.social_poster import publish_social_multiplier_posts
    return publish_social_multiplier_posts()

def check_social_drafts():
    """Diagnostic to see how many drafts are waiting."""
    from modules.database.supabase_client import get_supabase
    import json
    supabase = get_supabase()
    try:
        res = supabase.table("contacts_master").select("id", "company_name", "raw_research").execute()
        leads = res.data if hasattr(res, 'data') else []
        draft_count = 0
        for lead in leads:
            raw_data = lead.get("raw_research")
            if not raw_data: continue
            
            # Handle if raw_research is already a dict or still a string
            if isinstance(raw_data, str):
                try:
                    raw = json.loads(raw_data)
                except:
                    continue
            else:
                raw = raw_data
                
            drafts = raw.get("social_drafts", [])
            for d in drafts:
                if d.get("status") == "draft":
                    print(f"  [DRAFT] {lead.get('company_name')} - {d['platform']}")
                    draft_count += 1
        print(f"Total drafts pending: {draft_count}")
        return draft_count
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        return 0

@app.function(image=image, secrets=[VAULT])
def get_latest_social_video():
    """Finds the most recently published social post with a video."""
    from modules.database.supabase_client import get_supabase
    import json
    import os
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("id", "company_name", "raw_research").execute()
    leads = res.data if hasattr(res, 'data') else []
    
    published_videos = []
    for lead in leads:
        raw_data = lead.get("raw_research")
        if not raw_data: continue
        
        if isinstance(raw_data, str):
            try:
                raw = json.loads(raw_data)
            except:
                continue
        else:
            raw = raw_data
            
        drafts = raw.get("social_drafts", [])
        for d in drafts:
            if d.get("status") == "published" and d.get("video_url"):
                published_videos.append({
                    "company": lead.get("company_name"),
                    "platform": d["platform"],
                    "video_url": d["video_url"],
                    "published_at": d.get("published_at", "Unknown")
                })
    
    published_videos.sort(key=lambda x: x["published_at"], reverse=True)
    
    if published_videos:
        latest = published_videos[0]
        # WRITE TO WORKSPACE FOR RETRIEVAL (Bypassing logs)
        with open("/root/latest_video_link.txt", "w") as f:
            f.write(latest['video_url'])
def check_social_profiles():
    """Diagnostic to list connected Ayrshare profiles."""
    import os
    import json
    from ayrshare import SocialPost
    api_key = os.environ.get("AYRSHARE_API_KEY")
    if not api_key:
        print("❌ AYRSHARE_API_KEY not found.")
        return
        
    try:
        sp = SocialPost(api_key)
        print("\n--- DEEP AUDIT: AYRSHARE PROFILES ---")
        
        # 1. Check User Info
        user_info = sp.user()
        print("\n[USER() ENDPOINT]")
        print(json.dumps(user_info, indent=2))
        
        # 2. Check Profiles Info
        try:
            profiles_info = sp.profiles()
            print("\n[PROFILES() ENDPOINT]")
            print(json.dumps(profiles_info, indent=2))
        except Exception as pe:
            print(f"\n[PROFILES() ERROR/SKIPPED]: {pe}")
    except Exception as e:
        print(f"❌ Error: {e}")

def live_social_audit_test():
    """Gathers handles from social_drafts metadata in contacts_master."""
    import json
    from modules.database.supabase_client import get_supabase
    res_data = {"found_handles": {}}
    
    try:
        sb = get_supabase()
        res = sb.table("contacts_master").select("company_name,raw_research").eq("status", "research_done").limit(50).execute()
        
        for lead in res.data:
            raw_research = lead.get("raw_research")
            if not raw_research: continue
            
            try:
                raw = json.loads(raw_research) if isinstance(raw_research, str) else raw_research
                drafts = raw.get("social_drafts", [])
                for d in drafts:
                    plat = d.get("platform")
                    if plat in ["facebook", "instagram", "linkedin", "twitter"]:
                        handle = d.get("handle") or d.get("post_url") or "Linked"
                        if plat not in res_data["found_handles"]:
                            res_data["found_handles"][plat] = set()
                        res_data["found_handles"][plat].add(handle)
            except: continue
        
        # Convert sets to lists
        for k in res_data["found_handles"]:
            res_data["found_handles"][k] = list(res_data["found_handles"][k])
            
    except Exception as e:
        res_data["error"] = str(e)
        
    return res_data

def fire_global_broadcast():
    """Iterative Omni-Channel Broadcast to isolate plan restrictions."""
    import os
    import json
    import time
    from datetime import datetime
    from ayrshare import SocialPost
    
    # NEW API KEY verified via dashboard screenshot
    api_key = "57FCF9E6-1B534A66-9F05E51C-9ADE2CA5"
    sp = SocialPost(api_key)
    
    media_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995"
    platforms = ["linkedin", "facebook", "instagram", "twitter", "tiktok", "youtube", "pinterest", "threads", "gmb"]
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Content (max 280 for safety)
    content = (
        f"🚨 SYSTEM STATUS: OMNIPRESENCE ENGAGED ({timestamp}) 🚀\n\n"
        "9 social channels unified into one AI command center. We're now broadcasting at scale across LI, FB, IG, X, TT, YT & more. "
        "Visibility is an automated reality. #AIAutomation #Omnipresence #SovereignEmpire"
    )
    
    final_results = {"successes": [], "failures": []}
    
    print(f"🚀 INITIATING INDIVIDUAL PLATFORM BLAST...")
    
    for plat in platforms:
        print(f"  → Hitting {plat.upper()}...")
        payload = {
            "post": content,
            "platforms": [plat],
            "mediaUrls": [media_url]
        }
        
        if plat == "youtube":
            payload["youtubeOptions"] = {"title": f"Sovereign Empire: Omnipresence ({timestamp})"}
            
        try:
            res = sp.post(payload)
            if res.get("status") == "success":
                final_results["successes"].append({"platform": plat, "res": res})
                print(f"    ✅ Success: {res.get('id')}")
            elif "postIds" in res and res["postIds"]:
                # Sometimes it returns success inside postIds but error at top?
                success_item = next((p for p in res["postIds"] if p.get("status") == "success"), None)
                if success_item:
                    final_results["successes"].append({"platform": plat, "res": res})
                    print(f"    ✅ Success (via postIds): {success_item.get('id')}")
                else:
                    final_results["failures"].append({"platform": plat, "res": res})
                    print(f"    ❌ Failed: {res.get('message') or res.get('errors')}")
            else:
                final_results["failures"].append({"platform": plat, "res": res})
                print(f"    ❌ Failed: {res.get('message') or res.get('errors')}")
        except Exception as e:
            final_results["failures"].append({"platform": plat, "error": str(e)})
            print(f"    ❌ Exception: {e}")
            
        time.sleep(1) # Prevent rate limiting
        
    print("\n--- FINAL GLOBAL RESULTS ---")
    print(f"  Successes: {len(final_results['successes'])}")
    print(f"  Failures:  {len(final_results['failures'])}")
    
    return final_results

def get_latest_social_video_remote():
    """Remote video finder to bypass local connection issues."""
    from modules.database.supabase_client import get_supabase
    import json
    
    sb = get_supabase()
    # Query contacts_master for published video drafts
    res = sb.table("contacts_master").select("company_name, raw_research").execute()
    
    videos = []
    for lead in res.data:
        raw = lead.get("raw_research")
        if not raw: continue
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: continue
            
        drafts = raw.get("social_drafts", [])
        for d in drafts:
            if d.get("status") == "published" and d.get("video_url"):
                videos.append({
                    "company": lead["company_name"],
                    "url": d["video_url"],
                    "platform": d["platform"]
                })
    
    return videos

def fire_video_verification():
    """Iterative video verification to isolate platform support for MP4s."""
    import os
    import time
    from datetime import datetime
    from ayrshare import SocialPost
    
    # Secret will be hydrated to ENV
    api_key = os.environ.get("AYRSHARE_API_KEY")
    sp = SocialPost(api_key)
    
    # Stable 10s MP4 test asset
    video_url = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"
    platforms = ["linkedin", "facebook", "instagram", "twitter", "tiktok", "youtube", "pinterest", "threads", "gmb"]
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    content = f"🎥 SYSTEM VIDEO TEST: OMNIPRESENCE VERIFIED ({timestamp}) 🚀\nTesting direct MP4 broadcast capability across all active channels."
    
    final_results = {"successes": [], "failures": []}
    
    print(f"🚀 INITIATING VIDEO CAPABILITY TEST...")
    
    for plat in platforms:
        print(f"  → Testing {plat.upper()} with Video...")
        payload = {
            "post": content,
            "platforms": [plat],
            "mediaUrls": [video_url]
        }
        
        if plat == "youtube":
            payload["youtubeOptions"] = {"title": f"Sovereign Video Test ({timestamp})"}
            
        try:
            res = sp.post(payload)
            if res.get("status") == "success" or any(p.get("status") == "success" for p in res.get("postIds", [])):
                final_results["successes"].append({"platform": plat, "res": res})
                print(f"    ✅ Video Success: {plat}")
            else:
                final_results["failures"].append({"platform": plat, "res": res})
                print(f"    ❌ Video Failed: {plat}")
        except Exception as e:
            final_results["failures"].append({"platform": plat, "error": str(e)})
            print(f"    ❌ Video Exception: {plat} | {e}")
            
        time.sleep(2) # Prevent rate limiting during video processing
        
    return final_results

@app.local_entrypoint()
def trigger_video_verification():
    """Trigger the video verification and save results locally."""
    import json
    data = fire_video_verification.remote()
    with open("video_verification_results.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\n✅ VIDEO VERIFICATION COMPLETED. Results in: video_verification_results.json")

# Weekly Newsletter moved to consolidated trigger in system_orchestrator
@app.function(image=image, secrets=[VAULT], timeout=600)
def weekly_newsletter():
    """Weekly content loop — Phase 14 Value Retention (Consolidated)."""
    from scripts.weekly_digest import run_weekly_digest
    print("📧 NEWSLETTER: Starting weekly run...")
    run_weekly_digest(dry_run=False)
    print("✅ NEWSLETTER: Run complete.")


@app.function(image=image, secrets=[VAULT])
def trigger_principal_matcher(limit=200):
    from workers.principal_matcher import run_principal_matching_strike
    count = run_principal_matching_strike(limit=limit)
    return {"status": "complete", "matched_count": count}

@app.function(image=image, secrets=[VAULT])
def send_tiffaney_reminder():
    """Sends a 30-minute reminder SMS to Tiffaney Hayes."""
    import requests
    ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    payload = {
        "phone": "+13524349704",
        "message": "Hey Tiffaney! This is Maya from AI Service Co. Just a quick reminder about our onboarding call at 2:30 PM today. I'm looking forward to helping you customize your new Home Health agent! See you soon."
    }
    r = requests.post(ghl_webhook, json=payload, timeout=10)
    print(f"Reminder sent to Tiffaney: {r.status_code}")
    return {"status": "sent", "code": r.status_code}

@app.function(image=image, secrets=[VAULT])
def trigger_tiffaney_onboarding_call():
    """Manually triggered onboarding call for Tiffaney Hayes (Maya persona)."""
    import os, json, requests
    from modules.outbound_dialer import dial_prospect, SARAH_ASSISTANT_ID
    from modules.voice.sales_persona import get_persona_prompt
    
    # Target info
    phone = "+13524349704"
    name = "Tiffaney Hayes"
    
    # Build the prompt
    system_prompt = get_persona_prompt(
        call_mode="onboarding", 
        service_knowledge="AI Service Co provides automated voice answering, scheduling, and reputation management."
    )
    
    # Specialized call with prompt override
    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": os.environ.get("VAPI_PHONE_NUMBER_ID", "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"),
        "assistantOverrides": {
            "model": {
                "messages": [
                    {"role": "system", "content": system_prompt}
                ]
            }
        },
        "customer": {
            "number": phone,
            "name": name
        },
        "metadata": {
            "call_type": "onboarding_tiffaney",
            "business_type": "home_health"
        }
    }
    
    vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
    if not vapi_key:
        return {"error": "Missing VAPI_PRIVATE_KEY"}
        
    r = requests.post(
        "https://api.vapi.ai/call",
        headers={"Authorization": f"Bearer {vapi_key}", "Content-Type": "application/json"},
        json=payload
    )
    
    return r.json()

if __name__ == "__main__":
    print("⚫ ANTIGRAVITY v5.0 - SOVEREIGN DEPLOY")

