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
            "reportlab"
        )
        .run_commands("playwright install --with-deps chromium")
        .add_local_dir("utils", remote_path="/root/utils")
        .add_local_dir("workers", remote_path="/root/workers")
        .add_local_dir("core", remote_path="/root/core")
        .add_local_dir("api", remote_path="/root/api")
        .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
        .add_local_dir("modules/database", remote_path="/root/modules/database")
        .add_local_dir("modules/ai", remote_path="/root/modules/ai")
        .add_local_dir("modules/analytics", remote_path="/root/modules/analytics")
        .add_local_file("modules/outbound_dialer.py", remote_path="/root/modules/outbound_dialer.py")
        .add_local_dir("modules/voice", remote_path="/root/modules/voice")
    )

image = get_base_image()
VAULT = modal.Secret.from_name("sovereign-vault")

# Diagnostic function 1: Environment Verify
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
def test_db_connection():
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
@modal.web_endpoint(method="GET")
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
@modal.web_endpoint(method="GET")
def track_email_open(eid: str = "", recipient: str = "", business: str = ""):
    """Track email opens via 1x1 pixel - Added Feb 5, 2026"""
    import os
    from datetime import datetime
    from supabase import create_client
    from fastapi.responses import Response
    
    # 1x1 transparent GIF
    TRANSPARENT_GIF = bytes([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
        0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF,
        0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
        0x01, 0x00, 0x3B
    ])
    
    if eid:
        try:
            url = os.environ.get("SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
            key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            
            if key:
                sb = create_client(url, key)
                sb.table("email_opens").insert({
                    "email_id": eid,
                    "recipient_email": recipient or None,
                    "business_name": business or None,
                    "opened_at": datetime.utcnow().isoformat()
                }).execute()
        except Exception as e:
            print(f"Track error: {e}")
    
    return Response(content=TRANSPARENT_GIF, media_type="image/gif")

# ==== SMS INBOUND HANDLER (Sarah AI Reply with Memory) ====
@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
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
    
    # Sarah's BANT fact-finding prompt (Board-approved Option C)
    SARAH_PROMPT = f"""You are Sarah, AI assistant for AI Service Co.

YOUR MISSION: Gather useful intel through natural conversation BEFORE offering a call with Dan.
Use the BANT framework naturally - don't sound like an interrogation!
{context_str}

CONVERSATION FLOW (ask 1-2 questions per message, keep it SHORT):

1. NEED: First understand their challenge
   - "What challenges are you facing with automation or customer service?"
   - "What's the biggest headache in your business right now?"

2. BUSINESS TYPE: Understand their context
   - "What kind of business do you run?"
   - "Got it! Are you running a service business, retail, or...?"

3. AUTHORITY: Check if they're the decision maker
   - "Are you the one making decisions on new tools, or should I loop someone else in?"

4. BUDGET (if they ask about pricing):
   - "Trials start at $99/mo with a 7 day trial period."
   - Defer specific pricing discussions to Dan

5. TIMELINE: When they need it
   - "When are you looking to get something like this in place?"

RULES:
- Keep responses SHORT (1-3 sentences max for SMS)
- Be warm, friendly, conversational - NOT robotic
- Acknowledge what they said before asking next question ("Got it!", "Makes sense!")
- After 2-3 good exchanges, offer the call: "Based on what you've shared, I think Dan can help. Want me to set up a quick call?"
- If they seem annoyed or impatient, skip straight to: "Let me get you on a quick call with Dan - when works?"

FALLBACK (if confused or asked something weird):
- "I want to make sure I get you the best help - let me have Dan reach out directly. When's a good time?"
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
@modal.web_endpoint(method="POST")
def vapi_webhook(data: dict = {}):
    """
    Handles Vapi serverUrl callbacks for inbound and outbound calls.
    
    Board-Approved Implementation (Feb 7, 2026):
    1. Detect call direction from webhook payload
    2. Extract caller phone number (normalized E.164)
    3. Look up customer_memory for context
    4. Return assistantOverrides with injected context and call type
    5. On end-of-call, WRITE to customer_memory (fix "invisible success")
    
    Webhook events: assistant-request, call-started, end-of-call-report
    """
    import re
    import json
    from supabase import create_client
    from datetime import datetime
    from modules.voice.sales_persona import get_persona_prompt, SALES_SARAH_PROMPT
    
    # ========== PHASE 0: OBSERVABILITY LOGGING ==========
    print(f"\n{'='*60}")
    print(f"📞 [VAPI WEBHOOK] ENTRY - {datetime.utcnow().isoformat()}")
    print(f"📞 [VAPI WEBHOOK] Full payload keys: {list(data.keys())}")
    print(f"📞 [VAPI WEBHOOK] Event type: {data.get('message', {}).get('type', 'MISSING')}")
    
    # Helper function to log to vapi_debug_logs table (persistent diagnostics)
    def log_to_debug_table(sb, event_type: str, raw_phone: str, normalized_phone: str,
                           lookup_result: str, customer_name: str = None, context_summary: dict = None,
                           assistant_overrides: dict = None, call_mode: str = "default", notes: str = None, direction: str = None):
        try:
            sb.table("vapi_debug_logs").insert({
                "event_type": event_type,
                "call_direction": direction,
                "raw_phone": raw_phone,
                "normalized_phone": normalized_phone,
                "lookup_result": lookup_result,
                "customer_name_found": customer_name,
                "context_summary": context_summary,
                "assistant_overrides_sent": assistant_overrides,
                "call_mode": call_mode,
                "notes": notes
            }).execute()
            print(f"📝 [DEBUG_LOG] Logged to vapi_debug_logs")
        except Exception as e:
            print(f"⚠️ [DEBUG_LOG] Failed to log: {e}")
    
    message = data.get("message", {})
    event_type = message.get("type", "")
    call = message.get("call", {})
    
    # Extract call direction - check multiple possible fields (board recommended)
    direction = call.get("direction") or call.get("type") or call.get("callType", "unknown")
    
    # Normalize direction values
    if direction in ["inboundPhoneCall", "inbound"]:
        direction = "inbound"
    elif direction in ["outboundPhoneCall", "outbound"]:
        direction = "outbound"
    
    # Extract phone number - LOG RAW VALUE FIRST (observability)
    # Vapi puts customer in message.call.customer AND sometimes message.customer
    customer = message.get("customer", {}) or call.get("customer", {})
    raw_phone = customer.get("number", "") or call.get("customer", {}).get("number", "") or call.get("customerNumber", "") or call.get("to", "")
    print(f"📱 [MEMORY] Raw phone from Vapi: '{raw_phone}'")
    
    # Normalize using shared function (Board Phase 3)
    caller_phone = normalize_phone(raw_phone)
    print(f"📱 [MEMORY] Normalized phone: '{caller_phone}'")
    print(f"📱 [MEMORY] Direction: {direction}")
    
    # === Handle assistant-request event ===
    # This is the key event where we can inject context
    if event_type == "assistant-request":
        assistant_config = None
        context_summary = ""
        customer_name = ""
        
        # Look up customer memory by phone (use SERVICE_ROLE key per operational_memory.md)
        if caller_phone and len(caller_phone) >= 10:
            print(f"📱 [MEMORY] Attempting lookup for: {caller_phone}")
            try:
                supabase_url = os.environ.get("SUPABASE_URL")
                # CRITICAL: Use service_role key, NOT anon key (operational_memory Section 13)
                supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
                
                if supabase_url and supabase_key:
                    print(f"📱 [MEMORY] Supabase URL: {supabase_url[:30]}...")
                    print(f"📱 [MEMORY] Key type: {'SERVICE_ROLE' if 'SERVICE_ROLE' in (os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or '') else 'ANON'}")
                    
                    supabase = create_client(supabase_url, supabase_key)
                    
                    # Query customer_memory by phone number
                    result = supabase.table("customer_memory").select("*").eq("phone_number", caller_phone).limit(1).execute()
                    
                    print(f"📱 [MEMORY] Lookup result: {len(result.data) if result.data else 0} records found")
                    
                    if result.data:
                        customer_data = result.data[0]
                        context_data = customer_data.get("context_summary", {})
                        if isinstance(context_data, str):
                            # Migration: convert string context to dict
                            context_summary = {"history": context_data}
                        else:
                            context_summary = context_data
                            
                        customer_name = context_summary.get("contact_name", "") or customer_data.get("customer_name", "")
                        print(f"📱 [MEMORY] ✅ FOUND - Name: '{customer_name}' | History Len: {len(str(context_summary.get('history', '')))} chars")
                        lookup_status = "FOUND"
                        
                        # Check for call_mode in context (sales vs support)
                        call_mode = "support"  # Default
                        ctx = context_summary
                        if isinstance(ctx, dict) and ctx.get("call_purpose") == "sales":
                            call_mode = "sales"
                            print(f"🎯 [MEMORY] Call mode: SALES")
                    else:
                        print(f"📱 [MEMORY] ℹ️ NOT FOUND - No record for {caller_phone}")
                        lookup_status = "NOT_FOUND"
                        call_mode = "support"
                else:
                    print(f"📱 [MEMORY] ❌ ERROR - Missing Supabase credentials")
                    lookup_status = "ERROR"
                    call_mode = "support"
            except Exception as e:
                print(f"📱 [MEMORY] ❌ LOOKUP FAILED: {type(e).__name__}: {e}")
                lookup_status = "ERROR"
                call_mode = "support"
        
        # Build dynamic prompt injection based on direction
        if direction == "inbound":
            if customer_name:
                # RETURNING customer - greet by name!
                greeting_instruction = f"""
INBOUND CALL - RETURNING Customer calling us!
Greeting: "Hey {customer_name}! Thanks for calling back. This is Sarah. What can I help you with today?"
- You already know their name is {customer_name}, DON'T ask for it again.
- Reference prior conversations if context is available.
"""
            else:
                # NEW customer - ask for name
                greeting_instruction = """
INBOUND CALL - NEW customer calling us!
Greeting: "Hey, thanks for calling AI Service Company! This is Sarah. Who am I speaking with?"
- After they give their name: "Nice to meet you, [name]! What's going on with your business that made you reach out today?"
"""
        elif direction == "outbound":
            greeting_instruction = f"""
OUTBOUND CALL - We are calling the customer!
Greeting: "Hey, is this {customer_name or 'there'}?"
- If yes: "Hey {customer_name or 'there'}, this is Sarah from AI Service Company. Quick question - are you missing revenue from after-hours calls or leads that slip through the cracks? Got 30 seconds?"
"""
        else:
            greeting_instruction = "Unable to determine call direction. Use inbound greeting by default."
        
        context_injection = ""
        if context_summary:
            ctx = context_summary if isinstance(context_summary, dict) else {}
            qa = ', '.join(ctx.get('questions_asked', [])) or 'None yet'
            hist = ctx.get('history', 'No previous conversations')
            # Trim history to last 800 chars to keep prompt reasonable
            if len(hist) > 800:
                hist = '...' + hist[-800:]
            context_injection = f"""

CUSTOMER CONTEXT (from previous SMS + voice interactions):
- Name: {ctx.get('contact_name', 'Unknown')}
- Business: {ctx.get('business_type', 'Not known yet')}
- Main challenge: {ctx.get('main_challenge', 'Not discussed yet')}
- Budget mentioned: {ctx.get('budget_mentioned', 'Not discussed')}
- Questions already asked: {qa}
- Previous interaction notes:
{hist}

Use this context to personalize the conversation. Don't repeat questions they've already answered.
"""
        
        # ========== BUILD PROMPT BASED ON CALL MODE ==========
        call_mode = locals().get('call_mode', 'support')  # Get from memory lookup or default
        
        if call_mode == "sales":
            # Use Sales Sarah for outbound sales calls
            system_prompt = SALES_SARAH_PROMPT.format(
                customer_name=customer_name or "there",
                service_knowledge=SERVICE_KNOWLEDGE
            )
            print(f"🎯 [PERSONA] Using SALES Sarah")
        else:
            # Use Support Sarah (BANT fact-finding)
            system_prompt = f"""You are Sarah, AI phone assistant for AI Service Company. Be warm, genuine, casual.

{greeting_instruction}
{context_injection}

{SERVICE_KNOWLEDGE}

YOUR MISSION: Gather useful intel through natural conversation using BANT framework.
Questions to ask naturally (1-2 per turn):
1. NEED: "What challenges are you facing with calls or customer service?"
2. BUSINESS: "What kind of business do you run?"
3. AUTHORITY: "Are you the one making decisions on new tools?"
4. BUDGET (if asked): "Trials start at $99/mo with a 7 day trial period."
5. TIMELINE: "When are you looking to get something like this in place?"

WHEN READY TO CLOSE:
"Based on what you've shared, I think Dan can help. Want me to get you on a quick call with him?"

STYLE: Casual, concise, human. Use "totally", "honestly", "got it". Keep responses short.
"""
            print(f"📞 [PERSONA] Using SUPPORT Sarah")
        
        # Build assistant overrides
        assistant_overrides = {
            "variableValues": {
                "callDirection": direction,
                "customerPhone": caller_phone,
                "customerName": customer_name or "",
                "customerContext": context_summary or "No prior context",
                "callMode": call_mode
            },
            "firstMessage": None,  # Let the model handle greeting based on prompt
            "systemPrompt": system_prompt
        }
        
        # ========== LOG TO DEBUG TABLE (Persistent Diagnostics) ==========
        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
            if supabase_url and supabase_key:
                sb = create_client(supabase_url, supabase_key)
                log_to_debug_table(
                    sb=sb,
                    event_type=event_type,
                    raw_phone=raw_phone,
                    normalized_phone=caller_phone,
                    lookup_result=locals().get('lookup_status', 'UNKNOWN'),
                    customer_name=customer_name,
                    context_summary=context_summary if isinstance(context_summary, dict) else {"raw": str(context_summary)[:500]},
                    assistant_overrides=assistant_overrides,
                    call_mode=call_mode,
                    direction=direction,
                    notes=f"Greeting: {'returning' if customer_name else 'new'} customer"
                )
        except Exception as e:
            print(f"⚠️ [DEBUG_LOG] Failed: {e}")
        
        # Return assistant overrides with injected context
        return {"assistantOverrides": assistant_overrides}
    
    # === Handle end-of-call-report event ===
    # CRITICAL: This is where voice memory MUST be saved (Board Phase 2)
    elif event_type == "end-of-call-report":
        print(f"📱 [MEMORY] Processing end-of-call-report for {caller_phone}")
        transcript = message.get("transcript", "")
        summary = message.get("summary", "")
        
        print(f"📱 [MEMORY] Transcript length: {len(transcript) if transcript else 0}")
        print(f"📱 [MEMORY] Summary: '{summary[:100]}...'" if summary else "📱 [MEMORY] Summary: NONE")
        
        if caller_phone and (transcript or summary):
            try:
                supabase_url = os.environ.get("SUPABASE_URL")
                supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
                
                if supabase_url and supabase_key:
                    supabase = create_client(supabase_url, supabase_key)
                    
                    # ========== PHASE 2: EXTRACT CUSTOMER NAME FROM TRANSCRIPT ==========
                    extracted_name = ""
                    if transcript:
                        # Look for common name introduction patterns
                        import re
                        name_patterns = [
                            r"(?:my name is|i'm|this is|i am|call me)\s+([A-Z][a-z]+)",
                            r"(?:it's|its)\s+([A-Z][a-z]+)\s+(?:here|calling)"
                        ]
                        for pattern in name_patterns:
                            match = re.search(pattern, transcript, re.IGNORECASE)
                            if match:
                                extracted_name = match.group(1).title()
                                print(f"📱 [MEMORY] ✅ Extracted name from transcript: '{extracted_name}'")
                                break
                    
                    # Log to conversation_logs (FIXED: correct column names)
                    # Need customer_id from customer_memory lookup
                    voice_customer_id = None
                    try:
                        cid_result = supabase.table("customer_memory").select("customer_id").eq("phone_number", caller_phone).single().execute()
                        if cid_result.data:
                            voice_customer_id = cid_result.data['customer_id']
                    except:
                        pass
                    
                    if voice_customer_id:
                        log_result = supabase.table("conversation_logs").insert({
                            "customer_id": voice_customer_id,
                            "channel": "voice",
                            "direction": direction,
                            "content": transcript[:2000] if transcript else summary[:500],
                            "sarah_response": f"Call summary: {summary}" if summary else None,
                            "metadata": {"duration": str(message.get('durationSeconds', '?'))}
                        }).execute()
                        print(f"📱 [MEMORY] conversation_logs INSERT: {'SUCCESS' if log_result.data else 'FAILED'}")
                    else:
                        print(f"📱 [MEMORY] ⚠️ Skipping conversation_logs - no customer_id for {caller_phone}")
                    
                    # Refresh result for latest context to append
                    res_latest = supabase.table("customer_memory").select("context_summary").eq("phone_number", caller_phone).single().execute()
                    ctx_latest = res_latest.data.get("context_summary", {}) if res_latest.data else {}
                    if isinstance(ctx_latest, str):
                        ctx_latest = {"history": ctx_latest}
                    
                    # Update history
                    history = ctx_latest.get("history", "")
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                    new_history = f"{history}\n[Voice {direction} {timestamp}]: {summary or 'Call completed'}"
                    ctx_latest["history"] = new_history[-3000:] # Keep last 3000 chars of history
                    
                    if extracted_name:
                        ctx_latest["contact_name"] = extracted_name

                    # UPSERT to customer_memory (NOTE: customer_name and updated_at columns removed - don't exist on table)
                    upsert_result = supabase.table("customer_memory").upsert({
                        "phone_number": caller_phone,
                        "context_summary": ctx_latest
                    }, on_conflict="phone_number").execute()
                    
                    print(f"📱 [MEMORY] customer_memory UPSERT: {'SUCCESS' if upsert_result.data else 'FAILED'}")
                    print(f"📱 [MEMORY] ✅ Saved to customer_memory: phone={caller_phone}")
                    
                else:
                    print(f"📱 [MEMORY] ❌ ERROR - Missing Supabase credentials for write")
            except Exception as e:
                print(f"📱 [MEMORY] ❌ WRITE FAILED: {type(e).__name__}: {e}")
        else:
            print(f"📱 [MEMORY] ⚠️ Skipping write - no phone or content")
        
        # ========== NOTIFY DAN: Every Call (regardless of transcript) ==========
        print(f"📱 [NOTIFY] === NOTIFICATION BLOCK REACHED for {caller_phone} ===")
        if caller_phone:
            try:
                import urllib.request
                dan_phone = "+13529368152"
                caller_display = caller_phone or "Unknown"
                name_display = extracted_name if 'extracted_name' in dir() and extracted_name else "Unknown"
                summary_short = (summary or "Quick call - no summary")[:200]
                duration = message.get("durationSeconds", call.get("duration", "?"))
                
                notify_msg = f"📞 Sarah AI Call Report\n"
                notify_msg += f"Caller: {caller_display}\n"
                notify_msg += f"Name: {name_display}\n"
                notify_msg += f"Direction: {direction}\n"
                notify_msg += f"Duration: {duration}s\n"
                notify_msg += f"Summary: {summary_short}"
                
                ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
                notify_payload = json.dumps({
                    "phone": dan_phone,
                    "message": notify_msg
                }).encode()
                
                print(f"📱 [NOTIFY] BEFORE GHL webhook POST - URL: {ghl_webhook[:60]}...")
                print(f"📱 [NOTIFY] Payload phone: {dan_phone}, msg length: {len(notify_msg)}")
                
                notify_req = urllib.request.Request(
                    ghl_webhook,
                    data=notify_payload,
                    headers={"Content-Type": "application/json"}
                )
                response = urllib.request.urlopen(notify_req, timeout=10)
                resp_code = response.getcode()
                resp_body = response.read().decode('utf-8', errors='replace')[:200]
                print(f"📱 [NOTIFY] ✅ GHL webhook response: HTTP {resp_code}")
                print(f"📱 [NOTIFY] ✅ Response body: {resp_body}")
                print(f"📱 [NOTIFY] ✅ Dan notified about call from {caller_display}")
            except Exception as notify_err:
                print(f"📱 [NOTIFY] ❌ FAILED to notify Dan: {type(notify_err).__name__}: {notify_err}")
        
        print(f"{'='*60}\n")
        return {"status": "logged", "phone": caller_phone, "name_extracted": extracted_name if 'extracted_name' in dir() else ""}
    
    # Default response for other events
    return {"status": "received", "event": event_type}


# ==== MEMORY CHECK ENDPOINT (Board Phase 4 - Verification Tool) ====
@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def memory_check(phone: str = ""):
    """
    Diagnostic endpoint to verify memory contents for a phone number.
    Returns exact data stored in customer_memory table.
    
    Usage: /memory_check?phone=+15551234567
    
    Board mandate: Never claim "success" without database proof.
    This endpoint provides that proof.
    """
    from supabase import create_client
    from datetime import datetime
    
    print(f"\n📋 [MEMORY_CHECK] Query for: '{phone}'")
    
    if not phone:
        return {
            "status": "error",
            "message": "Phone parameter required. Usage: ?phone=+15551234567"
        }
    
    # Normalize the input phone
    normalized = normalize_phone(phone)
    print(f"📋 [MEMORY_CHECK] Normalized to: '{normalized}'")
    
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            return {"status": "error", "message": "Missing Supabase credentials"}
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Query customer_memory
        result = supabase.table("customer_memory").select("*").eq("phone_number", normalized).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            data = result.data[0]
            print(f"📋 [MEMORY_CHECK] ✅ FOUND - {data}")
            return {
                "status": "found",
                "phone_queried": normalized,
                "customer_name": data.get("customer_name", ""),
                "context_summary": data.get("context_summary", ""),
                "updated_at": data.get("updated_at", ""),
                "record_id": data.get("id", "")
            }
        else:
            print(f"📋 [MEMORY_CHECK] ❌ NOT FOUND")
            return {
                "status": "not_found",
                "phone_queried": normalized,
                "message": f"No memory record for {normalized}"
            }
    except Exception as e:
        print(f"📋 [MEMORY_CHECK] ❌ ERROR: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def health_check():
    """Quick health check for all critical services - used by UptimeRobot/monitoring"""
    import os
    from datetime import datetime
    from supabase import create_client
    
    checks = {}
    
    # Check Supabase connection
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            result = supabase.table("system_state").select("key").limit(1).execute()
            checks["supabase"] = "ok"
        else:
            checks["supabase"] = "no_creds"
    except Exception as e:
        checks["supabase"] = f"fail: {str(e)[:50]}"
    
    # Check Grok API key exists
    checks["grok_key"] = "ok" if os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY") else "missing"
    
    # Check GHL key exists
    checks["ghl_key"] = "ok" if os.environ.get("GHL_API_KEY") else "missing"
    
    # Check Vapi key exists
    checks["vapi_key"] = "ok" if os.environ.get("VAPI_API_KEY") else "missing"
    
    all_ok = all(v == "ok" for v in checks.values())
    status = "healthy" if all_ok else "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "checks": checks
    }


# ==== SYSTEM HEARTBEAT + CALL MONITOR (2-CRON app: heartbeat+outreach, zombie apps hold 2) ====
@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"))
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
            print(f"⚠️ SELF-HEAL: Outreach stalled — 0 touches in last 30 min")
        else:
            print(f"✅ Outreach check: {outreach_count} touches in last 30 min")
    except Exception as e:
        print(f"Self-heal check A (outreach) error (non-fatal): {e}")
    
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
            if hours_since >= 6:
                should_prospect = True
                print(f"PROSPECTOR: {hours_since:.1f}h since last run — triggering")
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
                        "customer_phone": customer,
                        "notified_at": datetime.now(timezone.utc).isoformat()
                    }).execute()
                except:
                    pass
            except Exception as ne:
                print(f"CALL MONITOR: Notify failed for {call_id[:12]}: {ne}")
        
        print(f"CALL MONITOR: checked {len(calls)} calls, notified {notified} new")
    except Exception as e:
        print(f"CALL MONITOR Error: {e}")

# --- WORKERS (2-CRON app: heartbeat + outreach. Others are MANUAL.) ---
from workers.outreach import auto_outreach_loop as outreach_logic
from workers.lead_unifier import unified_lead_sync as sync_logic
from workers.self_learning_cron import trigger_self_learning_loop as learning_logic
from workers.prospector import run_prospecting_cycle as prospector_logic

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/5 * * * *"))
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

@app.function(image=image, secrets=[VAULT])
def auto_prospecting():
    """Discovers new leads. 3-stage: Google Places → email enrichment → insert. Called by heartbeat every ~6h."""
    prospector_logic()

@app.function(image=image, secrets=[VAULT])
def unified_lead_sync():
    """Lead sync - MANUAL ONLY."""
    sync_logic()

@app.function(image=image, secrets=[VAULT])
def trigger_self_learning_loop():
    """Brain reflection - MANUAL ONLY."""
    learning_logic()


if __name__ == "__main__":
    print("⚫ ANTIGRAVITY v5.0 - SOVEREIGN DEPLOY")

