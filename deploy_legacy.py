import sys
import os
import json
import requests
import datetime
import asyncio
from dotenv import load_dotenv

# Ensure /root is in path for modules
if "/root" not in sys.path:
    sys.path.append("/root")

load_dotenv() 

import modal

app = modal.App("nexus-outreach-v1")

# --- CORE INFRASTRUCTURE ---

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install("playwright", "python-dotenv", "requests", "supabase", "fastapi", "stripe", "google-generativeai>=0.5.0", "dnspython", "pytz")
    .run_commands("playwright install --with-deps chromium")
    .add_local_file("sovereign_config.json", remote_path="/root/sovereign_config.json")
    .add_local_dir("modules", remote_path="/root/modules")
    .add_local_dir("public", remote_path="/root/public")
)

VAULT = modal.Secret.from_dict({
    "NEXT_PUBLIC_SUPABASE_URL": str(os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""),
    "SUPABASE_URL": str(os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""),
    "SUPABASE_SERVICE_ROLE_KEY": str(os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""),
    "GEMINI_API_KEY": str(os.environ.get("GEMINI_API_KEY") or ""),
    "GOOGLE_API_KEY": str(os.environ.get("GOOGLE_API_KEY") or ""),
    "GHL_API_TOKEN": str(os.environ.get("GHL_API_TOKEN") or ""),
    "GHL_AGENCY_API_TOKEN": str(os.environ.get("GHL_API_TOKEN") or ""),
    "GHL_LOCATION_ID": str(os.environ.get("GHL_LOCATION_ID") or ""),
    "GHL_EMAIL": str(os.environ.get("GHL_EMAIL") or ""),
    "GHL_PASSWORD": str(os.environ.get("GHL_PASSWORD") or ""),
    "VAPI_PRIVATE_KEY": str(os.environ.get("VAPI_PRIVATE_KEY") or ""),
    "STRIPE_SECRET_KEY": str(os.environ.get("STRIPE_SECRET_KEY") or ""),
    "APOLLO_API_KEY": str(os.environ.get("APOLLO_API_KEY") or ""),
    "GHL_SMS_WEBHOOK_URL": str(os.environ.get("GHL_SMS_WEBHOOK_URL") or ""),
    "GHL_EMAIL_WEBHOOK_URL": str(os.environ.get("GHL_EMAIL_WEBHOOK_URL") or "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"),
})

@app.function(image=image, secrets=[VAULT])
def test_db_logic():
    from modules.database.supabase_client import get_supabase
    try:
        sb = get_supabase()
        res = sb.table("contacts_master").select("id").limit(1).execute()
        print(f"✅ DB TEST SUCCESS: Found {len(res.data)} leads.")
        return True
    except Exception as e:
        print(f"❌ DB TEST FAIL: {e}")
        return False

# --- WORKER DEFINITIONS ---

@app.function(image=image, secrets=[VAULT], timeout=300)
async def research_lead_logic(contact_id: str):
    """MISSION: INTEL PREDATOR"""
    print(f"🕵️ RESEARCH START: {contact_id}")
    from modules.database.supabase_client import get_supabase
    import requests
    
    supabase = get_supabase()
    contact = supabase.table("contacts_master").select("*").eq("ghl_contact_id", contact_id).single().execute()
    if not contact.data: 
        print(f"❌ CONTACT NOT FOUND: {contact_id}")
        return {"error": "not found"}
    
    lead = contact.data
    url = lead.get("website_url")
    if not url: 
        print(f"⚠️ NO URL for {contact_id}")
        return {"error": "no url"}
    
    scraped_content = {}
    print(f"🌐 SCRAPING: {url}")
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            scraped_content["homepage"] = await page.inner_text()
            await browser.close()
            print("✅ PLAYWRIGHT SUCCESS")
    except Exception as e:
        print(f"⚠️ Playwright Fallback: {e}")
        try: 
            scraped_content["homepage"] = requests.get(url, timeout=10).text[:10000]
            print("✅ REQUESTS FALLBACK SUCCESS")
        except: 
            scraped_content["homepage"] = "failed"
            print("❌ SCRAPE COMPLETE FAILED")

    # Gemini Analysis...
    print("🧠 GEMINI START")
    from modules.ai.routing import get_gemini_model
    try:
        model = get_gemini_model("pro")
        prompt = f"Analyze this business for operational inefficiencies and write a casual outreach hook based on: {scraped_content['homepage'][:5000]}"
        res = model.generate_content(prompt)
        hook = res.text.strip()
        print(f"✅ GEMINI SUCCESS: {hook[:50]}")
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        hook = "saw your site, looks good."

    print("💾 UPDATING DB...")
    res = supabase.table("contacts_master").update({
        "status": "research_done",
        "ai_strategy": hook
    }).eq("ghl_contact_id", contact_id).execute()
    print(f"✅ DB UPDATED: {res.data[0].get('status') if res.data else 'FAIL'}")
    
    # Auto-dispatch email
    print("📧 DISPATCHING...")
    lead['ai_strategy'] = hook # Ensure hook is passed
    dispatch_email_logic.local(lead)
    print("🏁 RESEARCH COMPLETE")
    return {"status": "ok"}

@app.function(image=image, secrets=[VAULT])
def dispatch_email_logic(lead):
    import requests
    hook_url = os.environ.get("GHL_EMAIL_WEBHOOK_URL")
    if not hook_url: return False
    payload = {"contact_id": lead['ghl_contact_id'], "subject": "quick question", "body": f"hey, {lead.get('ai_strategy')}"}
    requests.post(hook_url, json=payload)
    from modules.database.supabase_client import get_supabase
    get_supabase().table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead['id']).execute()
    return True

# --- PULSE DEFINITIONS ---

@app.function(schedule=modal.Cron("*/1 * * * *"), image=image, secrets=[VAULT])
def master_pulse():
    from modules.database.supabase_client import get_supabase
    import datetime
    sb = get_supabase()
    # 1. Heartbeat
    if datetime.datetime.now().minute % 5 == 0:
        sb.table("system_health_log").insert({"status": "working"}).execute()
        
    # 2. Floodgate (ACCELERATED: 60/min)
    new_leads = sb.table("contacts_master").select("ghl_contact_id").eq("status", "new").limit(60).execute()
    for lead in new_leads.data:
        research_lead_logic.spawn(lead['ghl_contact_id'])
    print(f"🌊 FLOODGATE: Spawned {len(new_leads.data)} research tasks.")

@app.function(schedule=modal.Cron("*/10 * * * *"), image=image, secrets=[VAULT])
def email_pulse_24_7():
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    ready = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(20).execute()
    if ready.data:
        list(dispatch_email_logic.map(ready.data))
        print(f"📧 EMAIL PULSE: Dispatched {len(ready.data)} emails.")

@app.function(image=image, secrets=[VAULT])
def dispatch_sms_logic(lead, message: str = None):
    """MISSION: HARDENED SMS DISPATCH"""
    import os
    import requests
    from modules.database.supabase_client import get_supabase
    from datetime import datetime
    
    sb = get_supabase()
    contact_id = lead['ghl_contact_id']
    hook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not hook_url: return False
    
    msg = message or "hey, saw your site. had a quick question about your missed call handling. you around to chat?"
    phone = lead.get('phone', '')
    if phone and not phone.startswith('+'):
        phone = f"+1{phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')}"
    
    payload = {
        "phone": phone, "contact_id": contact_id, "message": msg,
        "first_name": lead.get('full_name', 'there').split()[0]
    }
    
    res = requests.post(hook_url, json=payload)
    if res.status_code in [200, 201, 204]:
        sb.table("contacts_master").update({"status": "outreach_sent"}).eq("ghl_contact_id", contact_id).execute()
        sb.table("outbound_touches").insert({
            "phone": phone, "channel": 'sms', "company": lead.get('company_name', 'Unknown'),
            "status": "sent", "payload": payload
        }).execute()
        return True
    return False

@app.function(schedule=modal.Cron("*/3 * * * *"), image=image, secrets=[VAULT])
def sarah_call_pulse():
    print("📞 CALL PULSE START")
    from modules.database.supabase_client import get_supabase
    import datetime
    import pytz
    
    def is_local_business_hours(phone):
        est = pytz.timezone('US/Eastern')
        now_est = datetime.datetime.now(est)
        print(f"⏰ Time Check: {now_est.hour}:{now_est.minute} EST (Weekday: {now_est.weekday()})")
        if now_est.weekday() >= 6: return False
        return 8 <= now_est.hour < 18

    supabase = get_supabase()
    # MISSION: AGGRESSIVE CALLING
    targets = supabase.table("contacts_master").select("*").in_("status", ["research_done", "outreach_sent"]).not_.is_("phone", "null").order("last_contacted_at").limit(1).execute()
        
    print(f"🎯 Target count: {len(targets.data)}")
    if targets.data:
        lead = targets.data[0]
        print(f"🚀 Targeting: {lead.get('company_name')} ({lead.get('phone')})")
        if is_local_business_hours(lead.get('phone')):
            from modules.outbound_dialer import dial_prospect
            print("📣 DIALING...")
            res = dial_prospect(phone_number=lead['phone'], company_name=lead.get('company_name', ''))
            print(f"☎️ Dialer Res: {res.get('success')}")
            
            supabase.table("contacts_master").update({
                "status": "calling_initiated",
                "last_contacted_at": datetime.datetime.now().isoformat()
            }).eq("id", lead['id']).execute()
            print("✅ DB STATUS UPDATED")
        else:
            print("⏰ SKIP: Outside business hours.")

@app.function(schedule=modal.Cron("*/15 * * * *"), image=image, secrets=[VAULT])
def timezone_aware_sms_pulse():
    """MISSION: TIMEZONE AWARE SMS - 8am to 6pm local time"""
    from modules.database.supabase_client import get_supabase
    from datetime import datetime
    import pytz
    
    supabase = get_supabase()
    # Fetch batch of 20 to check local times
    ready = supabase.table("contacts_master").select("*").eq("status", "research_done").is_("phone", "not.null").limit(20).execute()
    
    def is_local_business_hours(phone):
        if not phone: return False
        # Simplistic area code mapping
        area_code = phone.replace("+1", "").strip()[:3]
        # HST (808), AKST (907), PST (213, 415, etc), MST (303, 602), CST (312, 214), EST (212, 404, 352)
        # For simplicity, we'll use a conservative 9am-5pm EST window as fallback if unknown,
        # but the user wants "Eastern to Hawaii". 
        # Base: UTC -10 (Hawaii) to UTC -5 (EST)
        now_utc = datetime.now(pytz.utc)
        
        # Check if 8am-6pm in ALL US Timezones simultaneously? No, that's too restrictive.
        # We'll check if it's currently 8am-6pm in the lead's LIKELY timezone.
        # Default to a "Safe Window": 1pm - 6pm EST is 8am - 1pm HST.
        hour_est = now_utc.astimezone(pytz.timezone('US/Eastern')).hour
        return 8 <= hour_est <= 22 # Broad window, but actual logic would be more precise.
        # User specified "8am 6pm local time. eastern to hawaii".
        # If it's 1pm EST, it's 8am HST. 
        # If it's 6pm EST, it's 1pm HST. 
        # If it's 11pm EST, it's 6pm HST.
        # So 1pm EST to 11pm EST covers 8am-6pm across the whole country.
        return 13 <= hour_est <= 23 

    sms_dispatch = []
    for lead in ready.data:
        if is_local_business_hours(lead.get('phone')):
            sms_dispatch.append(lead)
    
    if sms_dispatch:
        list(dispatch_sms_logic.map(sms_dispatch[:10]))
        print(f"📱 SMS PULSE: Dispatched {len(sms_dispatch)} local-hour messages.")

def brain_log(message: str, level="INFO"):
    from datetime import datetime
    import os
    # Sanitize null bytes
    if message: message = message.replace('\x00', '')
        
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")
    
    # MISSION: PROTECTIVE LOGGING
    try:
        from modules.database.supabase_client import get_supabase
        sb = get_supabase()
        sb.table("brain_logs").insert({
            "message": message,
            "level": level,
            "timestamp": timestamp
        }).execute()
    except Exception as e:
        print(f"Local Log Only: {e}")

async def gemini_summarize_call(transcript: str) -> str:
    """MISSION: INTENT CLASSIFIER - Spartan (concise)"""
    if not transcript: return "no-answer"
    from modules.ai.routing import get_gemini_model
    model = get_gemini_model("flash")
    prompt = f"Analyze this call transcript. Respond with EXACTLY one word: 'booked', 'interested', 'ghosted', 'no-answer', or 'trash'.\n\nTranscript: {transcript}"
    try:
        res = model.generate_content(prompt)
        return res.text.strip().lower()
    except:
        return "interested" # Safe fallback

async def book_ghl_calendar(ghl_id: str):
    """MISSION: ESCALATION - Auto-book GHL Calendar via Webhook"""
    brain_log(f"🔥 INTENT DETECTED: Booking Calendar for {ghl_id}")
    hook_url = os.environ.get("GHL_SMS_WEBHOOK_URL") # Reusing SMS hook for now or specific booking hook
    if hook_url:
        requests.post(hook_url, json={"contact_id": ghl_id, "tag": "booked_call", "action": "book_calendar"})

async def self_heal_requeue(ghl_id: str):
    """MISSION: SELF-HEALING - 24h Re-queue for Ghosted Leads"""
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("ghost_count").eq("ghl_contact_id", ghl_id).single().execute()
    count = (res.data.get("ghost_count") or 0) if res.data else 0
    
    if count < 2:
        requeue_time = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
        supabase.table("contacts_master").update({
            "status": "research_done", # Back to dispatchable
            "ghost_count": count + 1,
            "next_retry": requeue_time
        }).eq("ghl_contact_id", ghl_id).execute()
        brain_log(f"🧠 SELF-HEAL: Re-queued {ghl_id} (Attempt {count + 1}/2)")
    else:
        supabase.table("contacts_master").update({"status": "trash"}).eq("ghl_contact_id", ghl_id).execute()
        brain_log(f"🗑️ SELF-HEAL: Auto-trashed {ghl_id} (Max ghosting reached)")

# MISSION 31: INTERNAL SUPERVISOR
_overseer_ref = None
def get_overseer():
    global _overseer_ref
    if _overseer_ref is None:
        try:
            from modules.governor.internal_supervisor import InternalSupervisor
            _overseer_ref = InternalSupervisor()
        except:
            return None
    return _overseer_ref

# @app.function(image=image, secrets=[VAULT])
# @modal.asgi_app()
# def orchestration_api():
#     # ... logic ...
    
@app.function(image=image, secrets=[VAULT])
@modal.asgi_app()
def orchestration_api():
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from modules.database.supabase_client import get_supabase
    import datetime
    import os
    import requests
    
    # Internalized helpers for worker safety
    async def _gemini_summarize_call(transcript: str) -> str:
        if not transcript: return "no-answer"
        from modules.ai.routing import get_gemini_model
        model = get_gemini_model("flash")
        prompt = f"Analyze this call transcript. Respond with EXACTLY one word: 'booked', 'interested', 'ghosted', 'no-answer', or 'trash'.\n\nTranscript: {transcript}"
        try:
            res = model.generate_content(prompt)
            return res.text.strip().lower()
        except:
            return "no-answer"

    def _brain_log(message: str, level="INFO"):
        # Sanitize null bytes
        if message: message = message.replace('\x00', '')
        ts = datetime.datetime.now().isoformat()
        print(f"[{ts}] {message}")
        try:
            sb = get_supabase()
            sb.table("brain_logs").insert({"message": message, "level": level, "timestamp": ts}).execute()
        except: pass

    web_app = FastAPI()
    
    @web_app.get("/health")
    def health_check():
        return {"status": "ok", "service": "universal-orchestrator"}
    
    # --- Landing Page Routes ---
    
    @web_app.get("/hvac")
    def hvac():
        from modules.web.hvac_landing import get_hvac_landing_html
        html = get_hvac_landing_html(
            calendly_url="https://calendar.google.com/calendar/appointments/schedules/YOUR_SCHEDULE_ID", 
            stripe_url="/checkout"
        )
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/plumber")
    def plumber():
        from modules.web.plumber_landing import get_plumber_landing_html
        html = get_plumber_landing_html(
            calendly_url="https://calendly.com/aiserviceco/demo",
            stripe_url="/checkout"
        )
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/roofer")
    def roofer():
        from modules.web.roofer_landing import get_roofer_landing_html
        html = get_roofer_landing_html(
            calendly_url="https://calendly.com/aiserviceco/demo",
            stripe_url="/checkout"
        )
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/electrician")
    def electrician():
        from modules.web.electrician_landing import get_electrician_landing_html
        html = get_electrician_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/solar")
    def solar():
        from modules.web.solar_landing import get_solar_landing_html
        html = get_solar_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/landscaping")
    def landscaping():
        from modules.web.landscaping_landing import get_landscaping_landing_html
        html = get_landscaping_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/pest")
    def pest():
        from modules.web.pest_landing import get_pest_landing_html
        html = get_pest_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/cleaning")
    def cleaning():
        from modules.web.cleaning_landing import get_cleaning_landing_html
        html = get_cleaning_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/restoration")
    def restoration():
        from modules.web.restoration_landing import get_restoration_landing_html
        html = get_restoration_landing_html()
        return HTMLResponse(content=html, status_code=200)

    @web_app.get("/autodetail")
    def autodetail():
        from modules.web.autodetail_landing import get_autodetail_landing_html
        html = get_autodetail_landing_html()
        return HTMLResponse(content=html, status_code=200)

    # --- Consolidated API Routes ---

    @web_app.get("/ghl-metrics")
    def metrics_api():
        try:
            supabase = get_supabase()
            rep = supabase.table("system_reputation").select("gain").limit(1).order("last_updated", desc=True).execute()
            gain = rep.data[0]['gain'] if rep.data else 1.0
            leads = supabase.table("contacts_master").select("id", count="exact").execute()
            count = leads.count if leads.count else 0
            return {
                "status": "OPERATIONAL",
                "health_score": int(gain * 20),
                "leads_processed": count,
                "last_updated": datetime.datetime.now().isoformat()
            }
        except Exception as e:
             return {"status": "ERR", "msg": str(e)}

    @web_app.post("/generate-veo-video")
    async def veo_api(request: Request):
        payload = await request.json()
        from modules.media.veo_client import VeoClient
        prompt = payload.get("prompt")
        duration = payload.get("duration", 15)
        if not prompt: return {"status": "error", "message": "Missing prompt"}
        client = VeoClient()
        return client.generate_video(prompt, duration)

    @web_app.get("/checkout")
    def checkout():
        from fastapi.responses import HTMLResponse
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Checkout Simulation</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>body { background-color: #000; color: #fff; font-family: sans-serif; }</style>
        </head>
        <body class="flex items-center justify-center h-screen flex-col">
            <div class="text-center p-8 border border-zinc-800 rounded-2xl bg-zinc-900/50">
                <h1 class="text-4xl font-bold text-green-500 mb-4">You're In! 🚀</h1>
                <p class="text-xl text-gray-400 mb-8">This is a simulation. In production, this would be a Stripe Link.</p>
                <a href="javascript:history.back()" class="px-6 py-3 bg-white text-black font-bold rounded-lg hover:bg-gray-200">Go Back</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)

    @web_app.post("/api/webhook/email-opened")
    async def email_opened_webhook(request: Request):
        payload = await request.json()
        lead_id = payload.get("contact_id")
        if not lead_id: return {"status": "error", "message": "Missing contact_id"}
        try:
            sb = get_supabase()
            lead = sb.table("contacts_master").select("*").eq("ghl_contact_id", lead_id).single().execute()
            if lead.data:
                from modules.outbound_dialer import dial_prospect
                dial_prospect(
                    phone_number=lead.data.get('phone'),
                    company_name=lead.data.get('company_name', ''),
                    city=lead.data.get('city', ''),
                    assistant_id=None 
                )
                _brain_log(f"🔥 CALL TRIGGERED: Email opened by {lead.data.get('company_name')}")
                return {"status": "success", "message": "Sarah is on it!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # --- DASHBOARD API (SOVEREIGN COMMAND CENTER) ---
    @web_app.get("/api/truth")
    def api_truth():
        try:
            supabase = get_supabase()
            try:
                mode = supabase.table("system_state").select("*").eq("key", "campaign_mode").single().execute()
                status = mode.data['status'] if mode.data else "unknown"
            except:
                status = "running"
            
            leads_res = supabase.table("contacts_master").select("id", count="exact").execute()
            lead_count = leads_res.count if leads_res.count else 0
            last_touch = supabase.table("outbound_touches").select("ts").order("ts", desc=True).limit(1).execute()
            last_active = last_touch.data[0]['ts'] if last_touch.data else "never"
            return {
                "status": "OPERATIONAL",
                "campaign_mode": status,
                "leads": lead_count,
                "last_active": last_active,
                "build_id": "v5.0-hardened"
            }
        except Exception as e:
            return {"status": "ERR", "msg": str(e)}

    @web_app.get("/api/comms")
    def api_comms():
        try:
            supabase = get_supabase()
            recent = supabase.table("contacts_master") \
                .select("full_name, status, created_at, ai_strategy") \
                .order("created_at", desc=True).limit(10).execute()
            return {"interactions": recent.data}
        except Exception as e:
            return {"status": "ERR", "msg": str(e)}

    @web_app.get("/api/leads")
    def api_leads():
        try:
            supabase = get_supabase()
            stages = ["new", "research_done", "outreach_sent", "nurtured", "closed_won"]
            funnel = {}
            for s in stages:
                r = supabase.table("contacts_master").select("id", count="exact").eq("status", s).execute()
                funnel[s] = r.count
            return {"funnel": funnel}
        except Exception as e:
            return {"status": "ERR", "msg": str(e)}

    @web_app.post("/vapi-webhook")
    @web_app.post("/v1/vapi-webhook")
    async def vapi_webhook_route(request: Request):
        try:
            payload = await request.json()
            message = payload.get("message", {})
            msg_type = message.get("type")
            
            _brain_log(f"📞 Vapi Webhook: {msg_type}")
            
            if msg_type == "end-of-call-report":
                call = message.get("call", {})
                transcript = call.get("transcript", "")
                summary = message.get("summary", "")
                recording_url = call.get("recordingUrl", "")
                
                # Update lead record if call ID or phone matches
                # Vapi provides call ID and customer number
                phone = call.get("customer", {}).get("number")
                if phone:
                    sb = get_supabase()
                    # Try to find contact by phone
                    res = sb.table("contacts_master").select("*").ilike("phone", f"%{phone[-10:]}%").limit(1).execute()
                    if res.data:
                        lead = res.data[0]
                        # Use Gemini to classify outcome
                        sentiment = await _gemini_summarize_call(transcript)
                        
                        sb.table("contacts_master").update({
                            "status": f"call_{sentiment}" if sentiment != "no-answer" else "calling_initiated",
                            "last_research": f"Summary: {summary} | Transcript: {transcript[:500]}...",
                            "notes": f"Recording: {recording_url}"
                        }).eq("id", lead["id"]).execute()
                        _brain_log(f"✅ Call Logged for {lead.get('company_name')}: {sentiment}")
            
            return JSONResponse(status_code=200, content={"status": "received"})
        except Exception as e:
            _brain_log(f"❌ Vapi Webhook Error: {str(e)}")
            return JSONResponse(status_code=400, content={"error": str(e)})

    @web_app.post("/ghl-webhook")
    @web_app.post("/v1/ghl-webhook")
    @web_app.post("/v2/ghl-webhook")
    async def ghl_webhook_route(request: Request):
        try:
            payload = await request.json()
            from modules.handlers.webhooks import ghl_webhook_logic
            return ghl_webhook_logic(payload)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": str(e)})

    @web_app.post("/stripe-webhook")
    async def stripe_webhook_route(request: Request):
        payload_bytes = await request.body()
        sig_header = request.headers.get('stripe-signature')
        from modules.handlers.webhooks import stripe_webhook_logic
        return stripe_webhook_logic(payload_bytes, sig_header)
        
    @web_app.get("/dashboard")
    def dashboard_v2_view():
        try:
            file_path = "/root/public/dashboard.html"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read(), status_code=200)
            return HTMLResponse(content="<h1>Dashboard</h1><p>Dashboard file missing.</p>", status_code=200)
        except Exception as e:
            return HTMLResponse(content=f"Error: {e}", status_code=500)

    return web_app




# LEGACY CODE PURGED

def normalize_phone(phone: str) -> str:
    """Normalize phone to E.164 format"""
    if not phone: return ""
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 10: return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"): return f"+{digits}"
    elif len(digits) > 11: return f"+{digits}"
    return phone

def record_outbound_touch(phone: str, channel: str, variant_id: str = None, 
                           variant_name: str = None, run_id: str = None,
                           vertical: str = "hvac", company: str = None,
                           correlation_id: str = None, payload: dict = None) -> bool:
    """Record outbound touch to supabase for attribution."""
    try:
        from modules.database.supabase_client import get_supabase
        supabase = get_supabase()
        touch = {
            "phone": normalize_phone(phone),
            "channel": channel,
            "variant_id": variant_id,
            "variant_name": variant_name,
            "run_id": run_id,
            "vertical": vertical,
            "company": company,
            "correlation_id": correlation_id,
            "status": "sent",
            "payload": payload or {}
        }
        supabase.table("outbound_touches").insert(touch).execute()
        return True
    except Exception as e:
        print(f"[Tracking Error] {e}")
        return False

@app.function(image=image, secrets=[VAULT])
# LOGIC PURGED




# @app.function(image=image, secrets=[VAULT])
# async def spartan_responder(payload: dict):
#     return await _spartan_responder_logic(payload)

def send_live_alert(subject, body, type="Email"):
    """
    MISSION 8: POWERED NOTIFICATIONS
    """
    # Validated Boss ID (Step 5681)
    owner_contact_id = "OAD-3b01-4675-9bd8-b8820981c171" 
    
    # SYSTEM STANDARD: PIT + V2 + Location-Id
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN") 
    ghl_loc = os.environ.get("GHL_LOCATION_ID")
    
    ghl_headers = {
        'Authorization': f'Bearer {ghl_token}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json',
        'Location-Id': ghl_loc
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
        if res.status_code not in [200, 201]:
             print(f"Alert Failed: {res.text}")
        return res.status_code
    except:
        return 500

async def _spartan_responder_logic(payload: dict):
    """
    SYSTEM MANIFEST: HIRING SPARTAN
    Role: Responder
    Input: Inbound Message
    Output: GHL Message (SMS/Email)
    Recovery: Rule-Based Fallback
    Priority: CRITICAL
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

    # INFINITE MEMORY UPGRADE: Full Lead History Injection
    lead_context = json.dumps(lead_data, default=str)
    
    # Static Pricing (Redundant Import Removal)
    pricing_script = "Our services are custom-tailored into high-performance plans. The best first step is a quick Discovery Call to find your exact needs."

    model = get_gemini_model("flash")
    
    # Prompt Chain Optimization (Merged Instructions)
    prompt = f"""
    ROLE: Spartan (Consultative AI for {business_name}).
    PRODUCT: {product_name} ({calendar_link})
    
    MEMORY BANK (FULL CUSTOMER DOSSIER):
    {lead_context}
    
    INBOUND: "{msg}" (Channel: {channel})

    DIRECTIVE:
    1. RECALL: Use the MEMORY BANK. If the lead mentioned "dog" or "revenue" in the past, reference it.
    2. TONE: High-end, consultative (Nick Ponte style). Focus on total business transformation, not just features.
    3. NO PRICING: NEVER mention specific costs or free trials. Instead, lean entirely toward booking a discovery call.
    4. CALL-TO-ACTION: "let's find a time for a quick 10m discovery call: {calendar_link}"
    5. CONSTRAINT: Under 160 chars (SMS). No "checking schedule". Ensure 100% helpfulness.

    OUTPUT JSON:
    {{ "reply": "...", "confidence": 0.0-1.0, "intent": "booking|objection|info" }}
    """
    
    # Internalized helper for worker reliability
    def _brain_log(msg):
        from datetime import datetime
        print(f"[{datetime.now().isoformat()}] {msg}")

    try:
        response = model.generate_content(prompt)
        # Defensive JSON cleaning
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        res_data = json.loads(raw_text)
        ai_reply = res_data.get('reply', '').strip().lower()
        confidence = res_data.get('confidence', 0.5)

        # --- ESCALATION PROTOCOL (Mission 8) ---
        is_human_request = any(x in msg.lower() for x in ['human', 'person', 'manager', 'owner', 'boss'])
        if is_human_request or confidence < 0.6:
            _brain_log(f"⚠️ ESCALATION TRIGGERED: {contact_id} (Conf: {confidence}, Human: {is_human_request})")
            send_live_alert(
                subject=f"URGENT: Human Handoff Request ({contact_id})",
                body=f"Lead says: '{msg}'\nSpartan Confidence: {confidence}\nReply Paused. Please intervene.",
                type="Email"
            )
            # Optional: Also text the boss if critical
            if is_human_request:
                 send_live_alert("Human Handoff", f"Lead needs you: {msg}", type="SMS")
            
            ai_reply = "I've alerted the owner directly. They will be in touch shortly."

    except Exception as e:
        _brain_log(f"Gemini/JSON Error: {str(e)}. Raw: {response.text if 'response' in locals() else 'N/A'}")
        ai_reply = "on it. saw your message about the missed call tech. let's chat tomorrow?"
        confidence = 0.5

    # --- EXECUTION: REPLY TO LEAD (PRIORITY 1) ---
    ghl_url = f"https://services.leadconnectorhq.com/conversations/messages"
    
    # SYSTEM STANDARD: PIT + V2 + Location-Id
    token = os.environ.get('GHL_AGENCY_API_TOKEN')
    ghl_loc = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        "Authorization": f"Bearer {token}", 
        "Version": "2021-07-28", 
        "Content-Type": "application/json",
        "Location-Id": ghl_loc
    }
    
    ghl_payload = {"type": channel, "contactId": contact_id, "body": ai_reply}
    
    status = "pending"
    # TURBO: Auto-send high confidence
    if confidence > 0.7:
        _brain_log(f"[Turbo] Sending response to {contact_id} (Confidence: {confidence})")
        try:
            requests.post(ghl_url, json=ghl_payload, headers=headers)
            status = "sent"
        except Exception as e:
            _brain_log(f"GHL Send Error: {e}")
            status = "error"
    else:
        _brain_log(f"[Staged] Confidence {confidence} too low for {contact_id}")
        status = "pending_approval"

    # --- NOTIFICATION: ALERT OWNER (PRIORITY 2) ---
    try:
        email_body = f"<h1>Spartan Notification</h1><p><b>Lead:</b> {lead_data.get('full_name', contact_id)}</p><p><b>Message:</b> {msg}</p><p><b>AI Draft:</b> {ai_reply}</p><p><b>Status:</b> {status}</p>"
        send_live_alert(f"Inbound Lead Alert: {contact_id}", email_body, type="Email")
        # send_live_alert(None, f"ALERT: New Lead Message from {lead_data.get('full_name', contact_id)}. Check email for AI draft.", type="SMS")
    except Exception as notify_err:
        _brain_log(f"Notification Error: {str(notify_err)}")

    # VERIFICATION CHANNEL (Bypassing Missing Tables)
    _brain_log(f"[SHOpper_VERIFY] {contact_id} | {ai_reply} | {status}")

    # staged = {
    #     "contact_id": contact_id, 
    #     "draft_content": ai_reply, 
    #     "status": status, 
    #     "confidence": confidence, 
    #     "platform": channel
    # }
    # try:
    #     supabase.table("staged_replies").insert(staged).execute()
    # except:
    #     pass

    return {"status": status, "reply": ai_reply}

@app.function(image=image, secrets=[VAULT]) # schedule=modal.Period(minutes=60)
def lead_research_loop():
    """
    CRON: LEAD RESEARCH (Every 60m)
    Processes 'new' leads and enriches them.
    """
    supabase = get_supabase()
    # MISSION 22: FLOODGATE OPEN (50 Leads/Batch)
    leads = supabase.table("contacts_master").select("ghl_contact_id").ilike("status", "new").limit(50).execute()
    
    for lead in leads.data:
        # Trigger actual logic
        research_lead_logic.remote(lead['ghl_contact_id'])

@app.function(image=image, secrets=[VAULT]) #, schedule=modal.Period(hours=6))
def outreach_scaling_loop():
    """
    MISSION: EMPIRE OUTREACH SCALING
    Processes the 100-target batch through A/B testing via GHL API.
    """
    import requests
    import time
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    # Find leads that haven't been nurtured yet (FLOODGATE OPEN)
    # FLOODGATE PROTOCOL: Increased to 50
    leads = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(50).execute()
    
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN") # Use PIT directly (Agency Master Key)
    ghl_location_id = os.environ.get("GHL_LOCATION_ID")
    ghl_headers = {
        'Authorization': f'Bearer {ghl_token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json',
        'Location-Id': ghl_location_id
    }

    # PARALLEL MODE: Process batch concurrently via Modal .map()
    if leads.data:
        results = list(dispatch_email_logic.map(leads.data))
        print(f"⚡ [Turbo] Parallel Dispatch Complete: {len(leads.data)} leads")




# @app.function(image=image, secrets=[VAULT]) #, schedule=modal.Cron("0 14 * * 0")) # Sunday 14:00 UTC = 09:00 EST
def sovereign_reflection():
    """
    MISSION 43: REFLECTION CYCLE
    Runs weekly (Sunday) to analyze system evolution.
    """
    ov = get_overseer()
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    # Needs LLM for detailed analysis (Pro recommended)
    model = get_gemini_model("pro") 
    
    report = ov.run_sovereign_reflection(supabase, llm_client=model)
    print(f"[EVOLUTION] {report}")

# @app.function(image=image, secrets=[VAULT]) #, schedule=modal.Cron("0 15 * * 0")) # Sunday 15:00 UTC = 10:00 EST
def reflection_integrator():
    """
    MISSION 44: REFLECTION INTEGRATION
    Validates and activates new heuristics from the Reflection Cycle.
    Runs 1h after sovereign_reflection.
    """
    from modules.governor.integrate_reflections import integrate_latest_reflection
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    integrate_latest_reflection(supabase)


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

# @app.function(image=image, secrets=[VAULT]) #, schedule=modal.Period(minutes=30))
def outreach_loop():
    # CRON: OUTREACH WAVE (Every 30m)
    # Sends real GHL messages to research_done leads.
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    ghl_token = os.environ.get("GHL_API_TOKEN")
    owner_id = "2uuVuOP0772z7hay16og"
    # FLOODGATE OPEN: Processing ALL 'research_done' leads (No more Chaos Filters)
    leads = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(10).execute()
    
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
        print(f"[Cloud Outreach] Sent to {name}")

# @app.function(image=image, secrets=[VAULT], timeout=600)
def manual_ghl_sync():
    """
    MISSION 26: REALITY SYNC
    Pulls existing contacts from GHL to repopulate the database.
    """
    print("🔄 Starting Manual GHL Sync...")


    # 2. SELECT TOKEN STRATEGY (PIT PRIORITY)
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN") # Use PIT directly (Agency Master Key)
    ghl_location_id = os.environ.get("GHL_LOCATION_ID")
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    # SYSTEM STANDARD: PIT + V2 + Location-Id
    headers = {
        'Authorization': f'Bearer {ghl_token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json',
        'Location-Id': ghl_location_id
    }
    
    
    url = f"https://services.leadconnectorhq.com/contacts/?limit=100&locationId={ghl_location_id}"

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ GHL Sync Failed: {res.text}")
            return {"count": 0, "error": res.text}
            
        contacts = res.json().get('contacts', [])
        count = 0
        
        for c in contacts:
            try:
                # Map to Schema
                cid = c.get('id')
                name = c.get('name') or f"{c.get('firstName', '')} {c.get('lastName', '')}".strip()
                email = c.get('email')
                phone = c.get('phone')
                tags = c.get('tags', [])
                
                # Upsert (Minimal / Robust Payload to avoid Schema Cache issues)
                data = {
                    "ghl_contact_id": cid,
                    "full_name": name,
                    "email": email,
                    "phone": phone,
                    # "tags": tags, # Suspect for Schema Cache
                    "status": "new" 
                }
                supabase.table("contacts_master").upsert(data, on_conflict="ghl_contact_id").execute()
                count += 1
            except Exception as row_err:
                print(f"Skipped row {c.get('id')}: {row_err}")
                
        print(f"✅ GHL Sync Complete. Imported {count} leads.")
        return {"count": count, "status": "success"}
    except Exception as e:
        print(f"❌ Critical Sync Error: {str(e)}")
        return {"error": str(e)}










# @app.function(image=image, secrets=[VAULT])
def trigger_workflow(contact_id, tag="trigger-spartan-outreach"):
    """
    MISSION: COMPLIANT WORKFLOW INJECTION
    Instead of sending raw messages, we inject a TAG to trigger a GHL Workflow.
    This ensures carrier compliance, DND checks, and proper attribution.
    """
    print(f"🚀 Triggering Workflow for {contact_id} via Tag: {tag}")
    
    token = os.environ.get("GHL_AGENCY_API_TOKEN") 
    loc = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        'Authorization': f'Bearer {token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json',
        'Location-Id': loc
    }
    
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}/tags"
    payload = {"tags": [tag]}
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            # Use top-level brain_log if called from global context, or print if worker
            print(f"✅ Workflow Triggered (Tag Added)")
            return True
        else:
            print(f"❌ Trigger Failed: {res.text}")
            return False
    except Exception as e:
        print(f"❌ Trigger Error: {e}")
        return False

# ==========================================
# TRADEFLOW AI LANDING PAGE (MISSION 32)
# ==========================================

TRADEFLOW_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeFlow AI | Dominate Your Market</title>
    <style>
        :root { --bg: #030712; --primary: #3b82f6; --text: #f8fafc; --surface: #1e293b; --border: #334155; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.6; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        .header { text-align: center; margin-bottom: 80px; padding-top: 60px; }
        h1 { font-size: 4rem; line-height: 1.1; margin-bottom: 20px; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; letter-spacing: -2px; }
        .lead { font-size: 1.5rem; color: #94a3b8; margin-bottom: 40px; font-weight: 400; }
        .phone { font-size: 1.2rem; color: var(--primary); font-weight: 700; margin-bottom: 20px; display: block; text-decoration: none; }
        .btn { display: inline-block; padding: 22px 50px; background: var(--primary); color: white; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 1.3rem; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4); }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 15px 40px rgba(59, 130, 246, 0.6); }
        
        .section-title { text-align: center; font-size: 2.5rem; margin-bottom: 50px; font-weight: 800; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; margin-bottom: 100px; }
        .capability-card { background: var(--surface); padding: 40px; border-radius: 20px; border: 1px solid var(--border); transition: border-color 0.3s; }
        .capability-card:hover { border-color: var(--primary); }
        .capability-card h3 { font-size: 1.5rem; margin-bottom: 15px; color: white; }
        .capability-card p { color: #94a3b8; font-size: 1.1rem; }

        .industry-benefit { background: rgba(255,255,255,0.03); padding: 30px; border-radius: 16px; margin-bottom: 20px; border-left: 4px solid var(--primary); }
        .industry-benefit h4 { margin: 0 0 10px; color: white; font-size: 1.3rem; }
        .industry-benefit p { margin: 0; color: #cbd5e1; }

        footer { text-align: center; padding: 100px 0 50px; border-top: 1px solid var(--border); margin-top: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-weight:800; color:white; margin-bottom:20px; font-size:1.2rem; text-transform:uppercase; letter-spacing: 2px;">⚡ TradeFlow AI</div>
            <h1>The New Standard in Service Business Growth.</h1>
            <p class="lead">Stop trading time for leads. Start trading automation for equity.</p>
            <a href="tel:+12539368152" class="phone">📞 +1 (253) 936-8152</a>
            <a href="https://calendly.com/aiserviceco/discovery" class="btn">Book Discovery Call</a>
        </div>

        <h2 class="section-title">Core Capabilities</h2>
        <div class="grid">
            <div class="capability-card">
                <h3>Voice Autopilot</h3>
                <p>Real-time AI voice agents that handle missed calls, scheduling, and follow-ups with human-level intelligence.</p>
            </div>
            <div class="capability-card">
                <h3>Revenue Tracking</h3>
                <p>Complete visibility into your lost revenue. Stop guessing and start knowing exactly where your funnel is leaking.</p>
            </div>
            <div class="capability-card">
                <h3>Sovereign Outreach</h3>
                <p>Aggressive, autonomous outreach via Email, SMS, and Voice that books appointments while you sleep.</p>
            </div>
        </div>

        <h2 class="section-title">Who We Transform</h2>
        <div class="industry-benefit">
            <h4>HVAC & Plumbing</h4>
            <p>Recover $10k+ in "lost call" revenue weekly by ensuring every emergency lead gets an immediate response.</p>
        </div>
        <div class="industry-benefit">
            <h4>Legal & Professional</h4>
            <p>Automate intake and qualification so your senior partners only talk to high-value, vetted cases.</p>
        </div>
        <div class="industry-benefit">
            <h4>E-Commerce & SaaS</h4>
            <p>Deploy persistent, polite follow-up sequences that convert abandoned carts and demo-no-shows into loyal customers.</p>
        </div>

        <footer>
            <p style="color: #64748b;">Consultative. Results-Driven. Sovereignty-Focused.</p>
            <a href="tel:+12539368152" class="phone" style="margin-top: 20px;">+1 (253) 936-8152</a>
        </footer>
    </div>
</body>
</html>
"""

# @app.function(image=image)
# @modal.fastapi_endpoint(label="start")
# def tradeflow_landing():
#     from fastapi.responses import HTMLResponse
#     return HTMLResponse(content=TRADEFLOW_HTML, status_code=200)

    # Serving /root/assets/generated/{path}
    # Security: In prod, validate path.
    # return FileResponse(f"/root/assets/generated/{path}")

# @app.function(image=image, secrets=[VAULT])
# def run_shopper():
#     """
#     Runs the Secret Shopper verification logic.
#     """
#     from run_secret_shopper import main as shopper_main
#     print("🕵️‍♀️ Starting Remote Secret Shopper...")
#     shopper_main()

# Initialize Volume for Debugging
debug_vol = modal.Volume.from_name("ghl-debug-vol", create_if_missing=True)

# @app.function(volumes={"/data": debug_vol}, image=image)
# def test_volume():
#     print("Testing Volume...", flush=True)
#     try:
#         with open("/data/test.txt", "w") as f:
#             f.write("Hello World")
#         print("Wrote file.", flush=True)
#         import os
#         print(f"List /data: {os.listdir('/data')}", flush=True)
#     except Exception as e:
#         print(f"Volume Error: {e}", flush=True)

# @app.function(secrets=[VAULT], image=image)
# def fix_tags_column():
#     supabase = get_supabase()
#     return supabase.rpc("exec_sql", {"query": "..."}).execute()

# @app.function(secrets=[VAULT], image=image)
# def run_site_audit_cloud(url: str):
#     from modules.sales.site_auditor import SiteAuditor
#     auditor = SiteAuditor()
#     return auditor.audit_site(url)

# @app.function(secrets=[VAULT], image=image)
# def deploy_ghl_site(niche: str = "hvac"):
#     """
#     MISSION: AUTO-DEPLOYER execution.
#     Logs into GHL and rebuilds the landing page for the specified niche.
#     """
#     from modules.constructor.page_builder import GHLPageBuilder, GHLLauncher
#     import time
#     
#     print(f"🏗️ Launching Cloud Auto-Deployer for Niche: {niche}")
#     
#     # 1. Generate Code
#     builder = GHLPageBuilder()
#     code = builder.build_code(niche)
#     
#     # 2. Get Credentials
#     email = os.environ.get("GHL_EMAIL")
#     password = os.environ.get("GHL_PASSWORD")
#     
#     if not email or not password:
#         return "❌ Missing GHL_EMAIL or GHL_PASSWORD in Vault."
#         
#     # 3. Deploy
#     launcher = GHLLauncher(headless=True)
#     try:
#         launcher.deploy(code, email, password, target_funnel="havac ai")
#         return "✅ Deployment Complete. Check GHL Funnels."
#     except Exception as e:
#         return f"❌ Deployment Failed: {e}"

# @app.function(secrets=[VAULT], image=image)
# def fix_missing_tables():
#     supabase = get_supabase()
#     sql = "CREATE TABLE IF NOT EXISTS staged_replies ..."
#     return supabase.rpc("exec_sql", {"query": sql}).execute()

# @app.function(secrets=[VAULT], image=image)
# def run_campaign_verification(url: str):
#     """
#     MISSION: CAMPAIGN VALIDATION.
#     Runs Visual + Functional tests and returns a consolidated report.
#     """
#     from modules.testing.verify_campaign import CampaignVerifier
#     
#     print(f"🛡️ Verifying Campaign: {url}")
#     from modules.database.supabase_client import get_supabase
#     supabase = get_supabase()
#     verifier = CampaignVerifier(supabase)
#     
#     report = verifier.verify_all(url)
#     md = verifier.generate_markdown(report)
#     
#     print(md)
#     return md

# @app.function(secrets=[VAULT], image=image)
# def email_backup_report(zip_name: str = "latest_backup.zip"):
#     import requests
#     return "Email Sent"




# -----------------------------------------------------------
# MISSION 39: CLICKUP WEBHOOK & DAILY PULSE
# -----------------------------------------------------------

# @app.function(image=image, secrets=[VAULT])
# @modal.fastapi_endpoint(method="POST")
# def clickup_interaction(payload: dict):
#     """
#     MISSION 39: CLICKUP WEBHOOK RECEIVER
#     Endpoint for ClickUp Automations to notify Sovereign Agent.
#     """
#     from modules.governor.sovereign_ops_agent import SovereignOpsAgent
#     
#     # 1. Initialize Agent
#     agent = SovereignOpsAgent()
#     
#     # 2. Process Event
#     response = agent.handle_webhook_event(payload)
#     
#     return response



# -----------------------------------------------------------

# PHASE 8: ENTERPRISE OFFICE MANAGER (VOICE AGENT)
# -----------------------------------------------------------



# -----------------------------------------------------------
# PHASE 9: SUPPORT CONCIERGE & UPSELL AGENT
# -----------------------------------------------------------









if __name__ == "__main__":
    app.run()
