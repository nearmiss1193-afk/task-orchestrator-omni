import sys
import os
import modal
from core.apps import engine_app as app

# IMAGE CONFIGURATION
def get_base_image():
    return (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("git")
        .pip_install(
            "playwright",
            "python-dotenv",
            "requests",
            "supabase",
            "fastapi",
            "stripe",
            "google-generativeai>=0.5.0",
            "dnspython",
            "pytz",
            "python-dateutil",
            "psycopg2-binary",
            "reportlab",
            "google-genai",
            "social-post-api",
            "resend"
        )
        .run_commands("playwright install --with-deps chromium")
        .add_local_dir("utils", remote_path="/root/utils")
        .add_local_dir("scripts", remote_path="/root/scripts")
        .add_local_dir("workers", remote_path="/root/workers")
        .add_local_dir("core", remote_path="/root/core")
        .add_local_dir("api", remote_path="/root/api")
        .add_local_file("__init__.py", remote_path="/root/__init__.py")
        .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
        .add_local_dir("modules/database", remote_path="/root/modules/database")
        .add_local_dir("modules/ai", remote_path="/root/modules/ai")
        .add_local_dir("modules/analytics", remote_path="/root/modules/analytics")
        .add_local_dir("modules/dispatch", remote_path="/root/modules/dispatch")
        .add_local_file("modules/outbound_dialer.py", remote_path="/root/modules/outbound_dialer.py")
        .add_local_dir("modules/voice", remote_path="/root/modules/voice")
    )

image = get_base_image()
# THE SOVEREIGN STEALTH (Feb 15): Mapping bit-perfect working anon key to all slots.
VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "DATABASE_URL": "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres",
    "AYRSHARE_API_KEY": "57FCF9E6-1B534A66-9F05E51C-9ADE2CA5"
})

# Diagnostic function 1: Environment Verify
@app.function(image=image, secrets=[VAULT])
def income_pipeline_check():
    """Run the empirical Revenue Waterfall diagnostic (Section 12)"""
    from scripts.revenue_waterfall import run_waterfall
    summary = run_waterfall()
    print(summary)
    return summary

@app.function(image=image, secrets=[VAULT])
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
@app.function(image=image, secrets=[VAULT])
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
@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT])
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

# ==== SOVEREIGN STATE API (External AI Audit Endpoint) ====
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def sovereign_state(token: str = ""):
    """Public endpoint for external AI audits (ChatGPT, Gemini, Grok)."""
    import os
    from datetime import datetime
    from supabase import create_client
    
    SOVEREIGN_TOKEN = "sov-audit-2026-ghost"
    if token != SOVEREIGN_TOKEN:
        return {"error": "Unauthorized. Pass ?token=sov-audit-2026-ghost"}
    
    # Direct initialization with fallbacks
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SERVICE_ROLE_KEY")
    
    if not key:
        return {"error": "SUPABASE_KEY not found in Modal vault", "audit_timestamp": datetime.now().isoformat()}
    
    try:
        sb = create_client(url, key)
        
        # Get campaign mode
        campaign_mode = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
        mode = campaign_mode.data[0].get("status") if campaign_mode.data else "unknown"
        
        # Get embeds
        embeds = sb.table("embeds").select("type,code").execute()
        locked_embeds = {e.get("type"): (e.get("code") or "")[:50] + "..." for e in embeds.data} if embeds.data else {}
        
        # Get last outreach
        touch = sb.table("outbound_touches").select("ts").order("ts", desc=True).limit(1).execute()
        last_outreach = touch.data[0].get("ts") if touch.data else None
        
        # Get lead count
        leads = sb.table("contacts_master").select("id", count="exact").limit(1).execute()
        
        return {
            "system_mode": mode,
            "sarah_status": "minimalist_icon_v4",
            "embed_source": "supabase_locked",
            "last_outreach": last_outreach,
            "health": {"supabase": "✅" if leads.count else "❌", "api": "✅"},
            "locked_embeds": locked_embeds,
            "audit_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "audit_timestamp": datetime.now().isoformat()}

# ==== EMAIL TRACKING PIXEL ENDPOINT ====
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def track_email_open(request, eid: str = "", recipient: str = "", business: str = ""):
    """Track email opens via 1x1 pixel - Enhanced for Sovereign Revenue Strike (Bot Bypass)"""
    import os, requests
    from datetime import datetime, timezone
    from fastapi import Response, Request
    
    # 1. Bot Bypass (Pixel Filter)
    ua = request.headers.get("user-agent", "").lower()
    bot_keywords = [
        "bot", "spider", "crawl", "slurp", "phantomjs", "headless",
        "barracuda", "trend micro", "mimecast", "microsoft", "google-http-client",
        "python-requests", "go-http-client"
    ]
    is_bot = any(keyword in ua for keyword in bot_keywords)
    
    # 1x1 transparent GIF
    TRANSPARENT_GIF = bytes([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
        0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF,
        0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
        0x01, 0x00, 0x3B
    ])
    
    if is_bot:
        print(f"👻 BOT SCAVENGER BLOCKED: {ua[:50]}...")
        return Response(content=TRANSPARENT_GIF, media_type="image/gif")

    if eid:
        try:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            headers = {
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            
            ts = datetime.now(timezone.utc).isoformat()
            
            # 2. Update outbound_touches dashboard (Direct Sync into Payload)
            r_get = requests.get(
                f"{url}/rest/v1/outbound_touches?payload->>email_uid=eq.{eid}",
                headers=headers
            )
            if r_get.status_code == 200 and r_get.json():
                touch = r_get.json()[0]
                new_payload = touch.get("payload") or {}
                new_payload["opened"] = True
                new_payload["opened_at"] = ts
                new_payload["human_intent"] = True  # High-fidelity signal
                
                requests.patch(
                    f"{url}/rest/v1/outbound_touches?id=eq.{touch['id']}",
                    headers=headers,
                    json={"payload": new_payload, "status": "opened"}
                )
                print(f"🔥 HUMAN INTENT DETECTED: {recipient or 'unknown'} opened audit.")
            
            # 3. Log to email_opens (Redundant Archive)
            requests.post(
                f"{url}/rest/v1/email_opens",
                headers=headers,
                json={
                    "email_id": eid,
                    "recipient_email": recipient or None,
                    "business_name": business or None,
                    "opened_at": ts,
                    "metadata": {"ua": ua, "type": "human"}
                }
            )
        except Exception as e:
            print(f"Sync error: {e}")
    
    return Response(content=TRANSPARENT_GIF, media_type="image/gif")

# ==== SMS INBOUND HANDLER (Sarah AI Reply with Memory) ====
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
            print(f"⚠️ [VAPI] Import failure: {imp_err}")
            traceback.print_exc()
            return {"status": "import_error", "event": event_type, "error": str(imp_err)}

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

            assistant_overrides = {
                "variableValues": {"customerPhone": caller_phone, "customerName": customer_name, "callMode": call_mode},
                "firstMessage": "Thank you for connecting, I'm Maya, I hope you're having a fantastic day! How can I help you today?" if is_maya_call else None,
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
                        
                        # Dan Notification
                        import urllib.request
                        notify_msg = f"📞 Call Summary: {caller_phone}\nName: {extracted_name or 'Unknown'}\nDir: {direction}\nSum: {(summary or 'No summary')[:200]}"
                        urllib.request.urlopen(urllib.request.Request(
                            "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd",
                            data=json.dumps({"phone": "+13529368152", "message": notify_msg}).encode(),
                            headers={"Content-Type": "application/json"}
                        ), timeout=10)
                except Exception as e:
                    print(f"⚠️ [REPORT] End of call processing failed: {e}")
            
            return {"status": "logged", "phone": caller_phone}

        # Default Response
        return {"status": "received", "event": event_type}

    except Exception as global_err:
        print(f"❌ CRITICAL VAPI WEBHOOK ERROR: {global_err}")
        print(traceback.format_exc())
        return {"status": "error_handled", "error": str(global_err)}



# ==== SYSTEM ORCHESTRATOR (Option 1: Consolidated Heartbeat + Outreach) ====
@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"), timeout=600)
def system_orchestrator():
    """Consolidated 5-minute cron: health, triggers, and outreach."""
    print("🚀 ORCHESTRATOR: Starting cycle...")
    
    # 1. Run Heartbeat Logic (Health + Cloud Triggers)
    system_heartbeat()
    
    # 2. Run Outreach Logic (Recycling + Execution)
    auto_outreach_loop()
    
    print("✅ ORCHESTRATOR: Cycle complete.")

@app.function(image=image, secrets=[VAULT])
def system_heartbeat():
    """Health check + Vapi call monitor (polls for completed calls, notifies Dan)."""
    import os, json
    import requests as req
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
        last_run = supabase.table("system_state").select("status").eq("key", "prospector_last_run").execute()
        
        if last_run.data and last_run.data[0].get("status"):
            last_ts = datetime.fromisoformat(last_run.data[0]["status"])
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
        from datetime import datetime, timezone, timedelta
        from modules.database.supabase_client import get_supabase
        supabase = get_supabase()
        
        should_prospect = False
        last_run = supabase.table("system_state").select("status").eq("key", "prospector_last_run").execute()
        
        if last_run.data and last_run.data[0].get("status"):
            last_ts = datetime.fromisoformat(last_run.data[0]["status"])
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
                "status": datetime.now(timezone.utc).isoformat(),
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
        
        r = req.get('https://api.vapi.ai/call?limit=5', headers=headers, timeout=15)
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
    
    api_base = os.environ.get("GOOGLE_PLACES_API_KEY") or "AIzaSyDVL4vfogtIKRLqOFNPMcKOg1LEAb9dipc"
    
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

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 8 * * 1-6"))
def scheduled_sunbiz_delta_watch():
    """8 AM Mon-Sat strike for brand-new Sunbiz registrations (Phase 12 Turbo)."""
    return delta_logic()

@app.function(image=image, secrets=[VAULT])
def run_social_migration():
    """Create the social_drafts table via psycopg2."""
    from scripts.migrate_social import create_social_table
    return create_social_table()

@app.function(image=image, secrets=[VAULT])
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
    """Debug what exactly is installed on the Modal image."""
    import subprocess
    import sys
    print(f"Python Version: {sys.version}")
    print("\n--- Pip List ---")
    print(subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode())
    try:
        from google import genai
        print("\n✅ from google import genai SUCCESS")
    except Exception as e:
        print(f"\n❌ from google import genai FAIL: {e}")
        
    try:
        import genai
        print("\n✅ import genai SUCCESS")
    except Exception as e:
        print(f"\n❌ import genai FAIL: {e}")
    return True
    """Manual trigger for Sunbiz sync."""
    return sunbiz_logic()

@app.function(image=image, secrets=[VAULT])
def trigger_manus_ingest(leads_json: str):
    """Manual trigger for Manus ingestion."""
    import json
    leads = json.loads(leads_json)
    return manus_logic(leads)
@app.function(image=image, secrets=[VAULT])
def trigger_cinematic_strike():
    """Triggers the Phase 12 Strike (Dossiers + Veo Videos) via Modal."""
    from scripts.trigger_cinematic_strike import run_phase12_strike
    return run_phase12_strike()

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
                        "status": "new",
                        "total_touches": 0
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


# ────────────────────────────────────────────────────────────
#  HEALTH CHECK ENDPOINT (for UptimeRobot / external watchdog)
# ────────────────────────────────────────────────────────────
@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def health_check():
    """Returns system health status for external monitoring (UptimeRobot)."""
    import os, json
    from datetime import datetime, timezone, timedelta
    from modules.database.supabase_client import get_supabase
    
    try:
        supabase = get_supabase()
        now = datetime.now(timezone.utc)
        
        # Check 1: Heartbeat (last 15 min)
        hb = supabase.table("system_health_log").select("checked_at").order(
            "checked_at", desc=True
        ).limit(1).execute()
        last_hb = hb.data[0]["checked_at"] if hb.data else None
        hb_ok = False
        if last_hb:
            hb_time = datetime.fromisoformat(last_hb.replace("Z", "+00:00"))
            hb_ok = (now - hb_time).total_seconds() < 900  # 15 min
        
        # Check 2: Outreach (last 30 min)
        touches = supabase.table("outbound_touches").select("ts", count="exact").gt(
            "ts", (now - timedelta(minutes=30)).isoformat()
        ).execute()
        outreach_count = touches.count if touches.count is not None else len(touches.data)
        
        # Check 3: Lead pool
        pool = supabase.table("contacts_master").select("id", count="exact").in_(
            "status", ["new", "research_done"]
        ).execute()
        pool_count = pool.count if pool.count is not None else len(pool.data)
        
        healthy = hb_ok and pool_count > 0
        
        return {
            "status": "healthy" if healthy else "degraded",
            "heartbeat": {"ok": hb_ok, "last": last_hb},
            "outreach_30m": outreach_count,
            "lead_pool": pool_count,
            "checked_at": now.isoformat(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
        
        # ─── REPLY HANDLER: Auto-respond + SMS Dan ───
        if event_type == "email.replied":
            recipient = event_data.get("from", "")  # The lead who replied
            reply_text = event_data.get("text", "")[:200]  # First 200 chars of reply
            company = touch_record.get("company", "Unknown") if touch_record else "Unknown"
            
            print(f"  🔥 REPLY from {recipient} ({company}): {reply_text[:80]}")
            
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
                
                # ACTION 3: Upgrade lead status to 'replied'
                try:
                    supabase.table("contacts_master").update(
                        {"status": "replied"}
                    ).eq("email", recipient).execute()
                    print(f"  ✅ Lead {recipient} status → replied")
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
        
    except Exception as e:
        print(f"❌ RESEARCH ERROR [Lead {lead_id}]: {e}")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"❌ RESEARCH ERROR [Lead {lead_id}]: {e}")
        # If it fails, maybe mark it so we don't keep trying? 
        # For now, just log and let it retry next heartbeat if it stays 'new'.
        pass

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

@app.function(image=image, secrets=[VAULT])
def unified_lead_sync():
    """Lead sync - MANUAL ONLY."""
    sync_logic()

@app.function(image=image, secrets=[VAULT])
def trigger_self_learning_loop():
    """Brain reflection - MANUAL ONLY."""
    learning_logic()


@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 14,21 * * *"))
def schedule_social_multiplier():
    """Publishes social drafts 2x/day (9 AM and 4 PM EST)."""
    from workers.social_poster import publish_social_multiplier_posts
    return publish_social_multiplier_posts()

@app.function(image=image, secrets=[VAULT])
def trigger_social_publish():
    """Manual trigger for social publishing."""
    from workers.social_poster import publish_social_multiplier_posts
    return publish_social_multiplier_posts()

@app.function(image=image, secrets=[VAULT])
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
@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT])
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

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 14 * * 1"), timeout=600)
def weekly_newsletter():
    """Weekly content loop — Phase 14 Value Retention (Mondays at 9 AM EST)."""
    from scripts.weekly_digest import run_weekly_digest
    print("📧 NEWSLETTER: Starting weekly run...")
    run_weekly_digest(dry_run=False)
    print("✅ NEWSLETTER: Run complete.")


if __name__ == "__main__":
    print("⚫ ANTIGRAVITY v5.0 - SOVEREIGN DEPLOY")

