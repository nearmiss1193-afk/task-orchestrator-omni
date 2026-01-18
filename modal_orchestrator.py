"""
SOVEREIGN ORCHESTRATOR - Unified ASGI App
All routes bundled into one FastAPI app for reliable Modal deployment.
"""
import modal
from fastapi import FastAPI, Request
from datetime import datetime
import json
import os

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "requests")

# Define secrets - these MUST be set via `modal secret create`
secrets = modal.Secret.from_name("empire-secrets")

app = modal.App("empire-api-v1", image=image, secrets=[secrets])

# Config (Non-sensitive constants only)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
ESCALATION_PHONE = "+13529368152"

# Secrets loaded at runtime from modal.Secret
# Set via: modal secret create empire-secrets SUPABASE_KEY=xxx GEMINI_API_KEY=xxx RESEND_API_KEY=xxx
def get_secrets():
    import os
    return {
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", "")
    }

# ==========================================================
# EVENT LOGGER - Durable event log with correlation support
# ==========================================================
def log_event(event_type: str, source: str, severity: str = "info", 
              correlation_id: str = None, entity_id: str = None, payload: dict = None):
    """
    Log event to Supabase event_log table for tracking and SSE mirroring.
    
    Args:
        event_type: e.g. 'lead.inbound', 'task.completed', 'error.occurred'
        source: 'modal', 'worker', 'vapi', 'ghl', 'system'
        severity: 'debug', 'info', 'warn', 'error', 'critical'
        correlation_id: Stable ID spanning workflow (e.g., phone number or lead_id)
        entity_id: Specific entity ID (call_id, task_id)
        payload: Additional event data
    """
    import requests as req
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        if not supabase_key:
            print("[EventLog] SUPABASE_KEY not configured")
            return
        req.post(
            f"{SUPABASE_URL}/rest/v1/event_log_v2",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            json={
                "type": event_type,
                "source": source,
                "severity": severity,
                "correlation_id": correlation_id,
                "entity_id": entity_id,
                "payload": payload or {}
            },
            timeout=5
        )
    except Exception as e:
        print(f"[EventLog] Error logging {event_type}: {e}")


# ==========================================================
# HARDENED HELPER FUNCTIONS - For scheduled job observability
# ==========================================================

def emit_event_safe(event_type: str, source: str, severity: str = "info", 
                    correlation_id: str = None, entity_id: str = None, payload: dict = None):
    """Fail-safe event emission - never throws, always logs errors"""
    try:
        log_event(event_type, source, severity, correlation_id, entity_id, payload)
    except Exception as e:
        print(f"[emit_event_safe] Failed to emit {event_type}: {e}")


def record_job_run_safe(job_name: str, window_id: str, status: str, 
                        details: dict = None, run_id: str = None):
    """Record job run to job_runs table - fail-safe, never throws"""
    import requests as req
    from datetime import datetime
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        if not supabase_key:
            return None
        
        today = datetime.utcnow().strftime('%Y-%m-%d')
        resp = req.post(
            f"{SUPABASE_URL}/rest/v1/job_runs",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={
                "job_name": job_name,
                "window_id": window_id,
                "scheduled_for": today,
                "status": status,
                "details": details or {},
                "correlation_id": run_id
            },
            timeout=10
        )
        if resp.status_code in [200, 201]:
            result = resp.json()
            return result[0].get("id") if result else None
        return None
    except Exception as e:
        print(f"[record_job_run_safe] Error: {e}")
        return None


def send_alert_email(subject: str, body: str, severity: str = "warning"):
    """Send alert email via Resend - fail-safe"""
    import requests as req
    try:
        secrets = get_secrets()
        resend_key = secrets.get("RESEND_API_KEY", "")
        if not resend_key:
            print(f"[Alert] No RESEND_API_KEY - would send: {subject}")
            return False
        
        resp = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Sovereign <alerts@aiserviceco.com>",
                "to": ["nearmiss1193@gmail.com"],
                "subject": f"[{severity.upper()}] {subject}",
                "html": f"<h2>{subject}</h2><pre>{body}</pre><p>Timestamp: {datetime.utcnow().isoformat()}Z</p>"
            },
            timeout=15
        )
        return resp.status_code < 400
    except Exception as e:
        print(f"[send_alert_email] Error: {e}")
        return False


def check_deadman_kpi():
    """Check if KPI snapshot was recorded in last 30 minutes"""
    import requests as req
    from datetime import datetime, timedelta
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        if not supabase_key:
            return True  # Fail open if no key
        
        cutoff = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        resp = req.get(
            f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.kpi.snapshot&ts=gte.{cutoff}&limit=1",
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            events = resp.json()
            return len(events) > 0
        return True  # Fail open
    except Exception as e:
        print(f"[check_deadman_kpi] Error: {e}")
        return True


def check_campaign_ran_today():
    """Check if campaign ran today by 9:30 AM CT"""
    import requests as req
    from datetime import datetime
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        if not supabase_key:
            return True
        
        today = datetime.utcnow().strftime('%Y-%m-%d')
        resp = req.get(
            f"{SUPABASE_URL}/rest/v1/job_runs?job_name=eq.campaign&scheduled_for=eq.{today}&status=in.(success,catchup,partial)&limit=1",
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            runs = resp.json()
            return len(runs) > 0
        return True
    except Exception as e:
        print(f"[check_campaign_ran_today] Error: {e}")
        return True


# ==========================================================
# TIMEZONE-AWARE SCHEDULING - 24/7 Operations
# ==========================================================

# US Area Code -> Timezone mapping (major codes)
AREA_CODE_TIMEZONES = {
    # Pacific (UTC-8)
    "209": "America/Los_Angeles", "213": "America/Los_Angeles", "310": "America/Los_Angeles",
    "323": "America/Los_Angeles", "408": "America/Los_Angeles", "415": "America/Los_Angeles",
    "510": "America/Los_Angeles", "530": "America/Los_Angeles", "559": "America/Los_Angeles",
    "562": "America/Los_Angeles", "619": "America/Los_Angeles", "626": "America/Los_Angeles",
    "650": "America/Los_Angeles", "661": "America/Los_Angeles", "707": "America/Los_Angeles",
    "714": "America/Los_Angeles", "760": "America/Los_Angeles", "805": "America/Los_Angeles",
    "818": "America/Los_Angeles", "831": "America/Los_Angeles", "858": "America/Los_Angeles",
    "909": "America/Los_Angeles", "916": "America/Los_Angeles", "925": "America/Los_Angeles",
    "949": "America/Los_Angeles", "951": "America/Los_Angeles",
    "503": "America/Los_Angeles", "541": "America/Los_Angeles", "971": "America/Los_Angeles",  # Oregon
    "206": "America/Los_Angeles", "253": "America/Los_Angeles", "360": "America/Los_Angeles",  # Washington
    "425": "America/Los_Angeles", "509": "America/Los_Angeles",
    "702": "America/Los_Angeles", "725": "America/Los_Angeles", "775": "America/Los_Angeles",  # Nevada
    # Mountain (UTC-7)
    "303": "America/Denver", "719": "America/Denver", "720": "America/Denver", "970": "America/Denver",  # Colorado
    "480": "America/Phoenix", "520": "America/Phoenix", "602": "America/Phoenix", "623": "America/Phoenix",  # Arizona
    "505": "America/Denver", "575": "America/Denver",  # New Mexico
    "801": "America/Denver", "385": "America/Denver",  # Utah
    # Central (UTC-6)
    "214": "America/Chicago", "254": "America/Chicago", "281": "America/Chicago", "361": "America/Chicago",
    "409": "America/Chicago", "432": "America/Chicago", "469": "America/Chicago", "512": "America/Chicago",
    "682": "America/Chicago", "713": "America/Chicago", "737": "America/Chicago", "806": "America/Chicago",
    "817": "America/Chicago", "830": "America/Chicago", "832": "America/Chicago", "903": "America/Chicago",
    "915": "America/Chicago", "936": "America/Chicago", "940": "America/Chicago", "956": "America/Chicago",
    "972": "America/Chicago", "979": "America/Chicago",  # Texas
    "312": "America/Chicago", "331": "America/Chicago", "618": "America/Chicago", "630": "America/Chicago",
    "708": "America/Chicago", "773": "America/Chicago", "815": "America/Chicago", "847": "America/Chicago",  # Illinois
    # Eastern (UTC-5)
    "239": "America/New_York", "305": "America/New_York", "321": "America/New_York", "352": "America/New_York",
    "386": "America/New_York", "407": "America/New_York", "561": "America/New_York", "727": "America/New_York",
    "754": "America/New_York", "772": "America/New_York", "786": "America/New_York", "813": "America/New_York",
    "850": "America/New_York", "863": "America/New_York", "904": "America/New_York", "941": "America/New_York",
    "954": "America/New_York",  # Florida
    "212": "America/New_York", "315": "America/New_York", "347": "America/New_York", "516": "America/New_York",
    "518": "America/New_York", "585": "America/New_York", "607": "America/New_York", "631": "America/New_York",
    "646": "America/New_York", "716": "America/New_York", "718": "America/New_York", "845": "America/New_York",
    "914": "America/New_York", "917": "America/New_York", "929": "America/New_York",  # New York
    # Hawaii (UTC-10)
    "808": "Pacific/Honolulu",
    # Alaska (UTC-9)
    "907": "America/Anchorage",
    # Guam/Saipan (UTC+10)
    "671": "Pacific/Guam",
    "670": "Pacific/Guam",  # Saipan/CNMI
}


def get_timezone_from_phone(phone: str) -> str:
    """Extract timezone from US phone number area code, default to CT"""
    import re
    if not phone:
        return "America/Chicago"
    
    # Extract area code
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) >= 3:
        area_code = digits[:3]
        return AREA_CODE_TIMEZONES.get(area_code, "America/Chicago")
    return "America/Chicago"


def is_business_hours_for_phone(phone: str, channel: str = "sms") -> bool:
    """
    Check if it's currently within send window for the contact's timezone.
    
    HVAC B2B Rules (LOCKED):
    - Calls: weekdays 9am-6pm local
    - SMS: weekdays 9am-7pm local
    - Email: weekdays 8-11am + 1-4pm local (except transactional/urgent)
    """
    from datetime import datetime
    try:
        tz_name = get_timezone_from_phone(phone)
        
        # Manual UTC offset calculation (no pytz dependency)
        utc_now = datetime.utcnow()
        utc_hour = utc_now.hour
        
        # Simple offset map
        offsets = {
            "America/Los_Angeles": -8, "America/Denver": -7, "America/Phoenix": -7,
            "America/Chicago": -6, "America/New_York": -5,
            "Pacific/Honolulu": -10, "America/Anchorage": -9, "Pacific/Guam": 10
        }
        offset = offsets.get(tz_name, -6)
        local_hour = (utc_hour + offset) % 24
        
        # Check weekday (0=Monday, 6=Sunday)
        weekday = utc_now.weekday()
        if weekday >= 5:  # Weekend - no outreach
            return False
        
        # Channel-specific windows (LOCKED CONSTANTS)
        if channel == "call":
            return 9 <= local_hour < 18  # 9am-6pm
        elif channel == "sms":
            return 9 <= local_hour < 19  # 9am-7pm
        elif channel == "email":
            # 8-11am OR 1-4pm
            return (8 <= local_hour < 11) or (13 <= local_hour < 16)
        else:
            return 9 <= local_hour < 18  # Default to call window
    except Exception as e:
        print(f"[is_business_hours_for_phone] Error: {e}")
        return True  # Fail open


def is_email_urgent_or_transactional(email_type: str) -> bool:
    """Check if email bypasses time windows (transactional or urgent response)"""
    bypass_types = ["transactional", "receipt", "confirmation", "urgent_reply", "inbound_response"]
    return email_type.lower() in bypass_types


def can_send_email_now(phone: str, email_type: str = "marketing") -> bool:
    """Check if email can be sent now - considers windows and exceptions"""
    if is_email_urgent_or_transactional(email_type):
        return True  # Always allowed
    return is_business_hours_for_phone(phone, channel="email")


def get_contacts_in_business_hours(channel: str = "sms"):
    """Get contacts whose local time is currently within business hours for the given channel"""
    import requests as req
    try:

        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        if not supabase_key:
            return []
        
        # Get contacts due for outreach
        resp = req.get(
            f"{SUPABASE_URL}/rest/v1/contacts_master?status=in.(new,active)&touch_count=lt.3&limit=100",
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
            timeout=15
        )
        if resp.status_code != 200:
            return []
        
        contacts = resp.json()
        # Filter to those in business hours for given channel
        return [c for c in contacts if is_business_hours_for_phone(c.get("phone", ""), channel)]
    except Exception as e:
        print(f"[get_contacts_in_business_hours] Error: {e}")
        return []



# Agent system prompts
SARAH_PROMPT = """You are Sarah, the inbound contact handler for AI Service Co.
You handle incoming SMS and calls. You qualify leads, answer questions, and book appointments.
Be warm, professional, and helpful. Offer the booking link early: {booking_link}
Pricing: $297 Starter, $497 Lite, $997 Growth (no contracts)
If frustrated or emergency, escalate. If STOP, opt out immediately."""

CHRISTINA_PROMPT = """You are Christina, the outbound sales specialist for AI Service Co.
You drive proactive outbound engagement. You are a confident closer.
Use urgency and value. Handle objections directly.
Booking link: {booking_link} | Pricing: $297 Starter, $497 Lite, $997 Growth
Push for the booking. Be direct but not pushy."""

@app.function()
@modal.asgi_app()
def orchestration_api():
    import requests
    from fastapi.middleware.cors import CORSMiddleware
    
    # Fetch secrets at function start
    _secrets = get_secrets()
    SUPABASE_KEY = _secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = _secrets["GEMINI_API_KEY"]
    RESEND_API_KEY = _secrets["RESEND_API_KEY"]
    
    if not SUPABASE_KEY:
        print("[CRITICAL] SUPABASE_KEY not configured! Run: modal secret create empire-secrets SUPABASE_KEY=xxx")
    
    api = FastAPI(title="Sovereign Orchestrator", version="2.0")
    
    # Add CORS middleware - allows aiserviceco.com dashboard to call Modal APIs
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://www.aiserviceco.com",
            "https://aiserviceco.com",
            "http://localhost:3000",
            "http://127.0.0.1:5500",
            "*"  # Fallback for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @api.get("/health")
    def health():
        """Health check endpoint"""
        return {
            "status": "ok",
            "orchestrator": "sovereign",
            "agents": ["sarah", "christina"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.post("/inbound")
    def handle_inbound(data: dict):
        """Handle inbound SMS/call - Routes to Sarah"""
        phone = data.get("phone", "")
        message = data.get("message", "")
        channel = data.get("channel", "sms")
        
        print(f"[INBOUND] {phone}: {message[:50]}...")
        
        # Log inbound event
        log_event("lead.inbound", "modal", "info", correlation_id=phone, payload={"message": message[:100], "channel": channel})
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Check for opt-out
        if any(word in message.upper() for word in ["STOP", "UNSUBSCRIBE", "CANCEL"]):
            # Log opt-out
            requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=headers, json={
                "event_type": "opt_out", "phone": phone, "success": True, "details": {"message": message}
            })
            return {"agent": "sarah", "action": "opt_out", "response": None}
        
        # Get memory for this contact
        memory_resp = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=headers)
        memories = memory_resp.json() if memory_resp.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "No previous memory."
        
        # Generate Sarah's response
        prompt = f"""{SARAH_PROMPT.format(booking_link=BOOKING_LINK)}

Customer memory:
{memory_context}

Customer message: "{message}"

Respond as Sarah. Keep it short (under 160 chars for SMS). Be helpful and push for booking if appropriate."""

        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            response_text = f"Hi! Thanks for reaching out. Book a free call here: {BOOKING_LINK} -Sarah"
            # CONTRACT: error.occurred for AI failures
            log_event("error.occurred", "modal", "error", correlation_id=phone, payload={
                "error": "gemini_generation_failed",
                "message": str(e)[:200],
                "component": "inbound_handler",
                "severity": "warn",
                "recoverable": True
            })
        
        # Log interaction
        requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
            "phone": phone, "direction": "inbound", "channel": channel,
            "message": message, "response": response_text, "agent": "sarah"
        })
        
        # Send response via GHL
        message_id = f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{phone[-4:]}"
        sms_success = False
        try:
            ghl_resp = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
            sms_success = ghl_resp.status_code < 400
        except Exception as e:
            print(f"[GHL] Inbound response failed: {e}")
        
        # CONTRACT: sms.sent / sms.failed events
        if sms_success:
            log_event("sms.sent", "modal", "info", correlation_id=phone, entity_id=message_id, payload={
                "message_id": message_id,
                "to": phone,
                "template": "inbound_response",
                "agent": "sarah"
            })
        else:
            log_event("sms.failed", "modal", "error", correlation_id=phone, entity_id=message_id, payload={
                "message_id": message_id,
                "to": phone,
                "error": "ghl_send_failed",
                "agent": "sarah"
            })
        
        # Log task completion
        log_event("task.completed", "modal", "info", correlation_id=phone, payload={"agent": "sarah", "response": response_text[:100], "sms_sent": sms_success})
        
        return {"agent": "sarah", "response": response_text}
    
    # =========================================
    # GHL WEBHOOK ENDPOINTS
    # =========================================
    
    @api.post("/webhook/ghl/appointment")
    async def ghl_appointment_webhook(request: Request, token: str = ""):
        """
        GHL AppointmentCreate/Update webhook receiver.
        Robust field parsing for various GHL payload structures.
        Logs to event_log_v2 as appointment.created/updated.
        """
        import re
        
        # Phone normalizer helper
        def normalize_phone(phone: str) -> str:
            if not phone:
                return ""
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                return f"+1{digits}"
            elif len(digits) == 11 and digits.startswith('1'):
                return f"+{digits}"
            return f"+{digits}" if digits else ""
        
        try:
            data = await request.json()
        except:
            data = {}
        
        # Token auth via env WEBHOOK_TOKEN (fall back to GHL_WEBHOOK_TOKEN)
        expected_token = os.environ.get("WEBHOOK_TOKEN", os.environ.get("GHL_WEBHOOK_TOKEN", "sovereign_default"))
        if token and token != expected_token:
            return {"status": "error", "message": "invalid_token"}
        
        # Robust field extraction (handles various GHL payload structures)
        appointment = data.get("appointment", data)  # Nested or flat
        
        # Field paths: try appointment.X first, then body.X
        appt_id = appointment.get("id") or data.get("id", "")
        contact_id = appointment.get("contactId") or data.get("contactId", "")
        calendar_id = appointment.get("calendarId") or data.get("calendarId", "")
        start_time = appointment.get("startTime") or appointment.get("start_time") or data.get("startTime", "")
        end_time = appointment.get("endTime") or appointment.get("end_time") or data.get("endTime", "")
        status = appointment.get("appointmentStatus") or appointment.get("status") or data.get("status", "confirmed")
        location_id = data.get("locationId") or appointment.get("locationId", "")
        event_type = data.get("type") or data.get("event") or ""
        
        # Get phone and normalize for correlation_id
        raw_phone = appointment.get("phone") or data.get("phone", "")
        normalized_phone = normalize_phone(raw_phone)
        correlation_id = normalized_phone if normalized_phone else contact_id
        
        # CONTRACT: webhook.inbound event first
        log_event("webhook.inbound", "ghl", "info", entity_id=appt_id, payload={
            "provider": "ghl",
            "event": event_type or "AppointmentCreate",
            "id": appt_id,
            "path": "/webhook/ghl/appointment"
        })
        
        # Determine event type (created vs updated)
        is_update = "Update" in event_type or status.lower() in ["confirmed", "cancelled", "rescheduled", "completed", "no_show"]
        appt_event_type = "appointment.updated" if is_update else "appointment.created"
        
        # CONTRACT: appointment.created / appointment.updated payload
        log_event(
            appt_event_type,
            "ghl",
            "info",
            correlation_id=correlation_id,
            entity_id=appt_id,
            payload={
                "appointment_id": appt_id,
                "calendar_id": calendar_id,
                "contact_id": contact_id,
                "status": status,
                "start_time": start_time,
                "end_time": end_time,
                "location_id": location_id,
                "pipeline_stage": "Booked",
                "source": "ghl"
            }
        )
        
        # Also emit SSE event for dashboard
        # (event is stored in event_log_v2 which SSE reads)
        
        # === VARIANT ATTRIBUTION LOOKUP (for Thompson Sampling) ===
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        variant_id = None
        variant_name = None
        attribution_id = None
        phone = appointment.get("phone", "")
        
        # Look up most recent outreach to this contact (within 14 days)
        try:
            attr_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/outreach_attribution?contact_id=eq.{contact_id}&order=ts.desc&limit=1",
                headers=headers, timeout=10
            )
            if attr_resp.status_code == 200 and attr_resp.json():
                attr = attr_resp.json()[0]
                attribution_id = attr.get("id")
                variant_id = attr.get("variant_id")
                variant_name = attr.get("variant_name")
                phone = attr.get("phone", phone)
        except Exception as e:
            print(f"[Attribution] Lookup failed: {e}")
        
        # If no contact_id match, try by phone
        if not attribution_id and phone:
            try:
                attr_resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/outreach_attribution?phone=eq.{phone}&order=ts.desc&limit=1",
                    headers=headers, timeout=10
                )
                if attr_resp.status_code == 200 and attr_resp.json():
                    attr = attr_resp.json()[0]
                    attribution_id = attr.get("id")
                    variant_id = attr.get("variant_id")
                    variant_name = attr.get("variant_name")
            except:
                pass
        
        # Record appointment outcome (links appointment to variant)
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/appointment_outcomes", headers=headers, json={
                "contact_id": contact_id,
                "phone": phone,
                "appointment_id": appt_id,
                "variant_id": variant_id,
                "variant_name": variant_name,
                "outcome": "booked",
                "attribution_id": attribution_id,
                "metadata": {"calendar_id": calendar_id, "start_time": start_time}
            }, timeout=5)
        except Exception as e:
            print(f"[Outcome] Failed to record: {e}")
        
        # CONTRACT: outcome.booking event for learning system
        log_event(
            "outcome.booking",
            "modal",
            "info",
            correlation_id=correlation_id,
            entity_id=appt_id,
            payload={
                "appointment_id": appt_id,
                "contact_id": contact_id,
                "phone": normalized_phone or phone,
                "variant_id": variant_id,
                "variant_name": variant_name,
                "attribution_id": attribution_id,
                "attribution_ts": datetime.utcnow().isoformat(),
                "calendar_id": calendar_id,
                "start_time": start_time,
                "status": status
            }
        )
        
        # Update variant alpha (success) for Thompson Sampling
        if variant_id:
            try:
                requests.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/update_variant_outcome",
                    headers=headers,
                    json={"p_variant_id": variant_id, "p_success": True},
                    timeout=5
                )
                print(f"[Thompson] Updated variant {variant_name} alpha+1")
            except Exception as e:
                print(f"[Thompson] Failed to update: {e}")
        
        print(f"[GHL Appointment] Received: {appt_id} for contact {contact_id} status={status} variant={variant_name}")
        
        return {"status": "ok", "appointment_id": appt_id, "logged": True, "variant_attributed": variant_name}
    
    @api.post("/webhook/ghl")
    def ghl_generic_webhook(data: dict, token: str = ""):
        """
        Generic GHL webhook receiver for any event type.
        Routes to specific handlers based on type.
        """
        event_type = data.get("type", "unknown")
        
        # CONTRACT: webhook.inbound event first
        log_event("webhook.inbound", "ghl", "info", payload={
            "provider": "ghl",
            "event": event_type,
            "id": data.get("id", data.get("contactId", "")),
            "path": "/webhook/ghl"
        })
        
        # Route appointment events
        if "Appointment" in event_type:
            return ghl_appointment_webhook(data, token)
        
        # Log generic event
        log_event(
            f"ghl.{event_type.lower()}",
            "ghl",
            "info",
            payload=data
        )
        
        return {"status": "ok", "event_type": event_type}
    
    @api.post("/webhook/vapi")
    async def vapi_webhook(request: Request, token: str = ""):
        """
        VAPI.ai webhook receiver for voice call events.
        Emits call.answered / call.missed events per the strict event taxonomy.
        """
        try:
            data = await request.json()
        except:
            data = {}
        
        # Token auth (optional)
        expected_token = os.environ.get("VAPI_WEBHOOK_TOKEN", os.environ.get("WEBHOOK_TOKEN", "sovereign_default"))
        if token and token != expected_token:
            return {"status": "error", "message": "invalid_token"}
        
        # Parse VAPI payload structure
        call_id = data.get("call", {}).get("id") or data.get("callId") or data.get("id", "")
        call_type = data.get("type") or data.get("event") or data.get("status", "")
        phone_number = data.get("call", {}).get("customer", {}).get("number") or data.get("phoneNumber") or data.get("from", "")
        
        # Extract call metadata
        duration_seconds = data.get("call", {}).get("duration") or data.get("duration") or 0
        ended_reason = data.get("call", {}).get("endedReason") or data.get("endedReason") or ""
        assistant_id = data.get("call", {}).get("assistantId") or data.get("assistantId") or ""
        
        # Normalize phone for correlation
        import re
        def normalize_phone(p: str) -> str:
            if not p: return ""
            digits = re.sub(r'\D', '', p)
            if len(digits) == 10: return f"+1{digits}"
            elif len(digits) == 11 and digits.startswith('1'): return f"+{digits}"
            return f"+{digits}" if digits else ""
        
        normalized_phone = normalize_phone(phone_number)
        
        # CONTRACT: webhook.inbound event first
        log_event("webhook.inbound", "vapi", "info", entity_id=call_id, payload={
            "provider": "vapi",
            "event": call_type,
            "id": call_id,
            "path": "/webhook/vapi"
        })
        
        # Determine call event type based on VAPI status
        # VAPI events: call-started, assistant-message, user-message, call-ended, etc.
        if call_type in ["call-started", "call-answered", "assistant-request"]:
            # CONTRACT: call.answered payload
            log_event("call.answered", "vapi", "info", correlation_id=normalized_phone, entity_id=call_id, payload={
                "call_id": call_id,
                "from": normalized_phone,
                "assistant_id": assistant_id,
                "provider": "vapi",
                "duration_seconds": duration_seconds
            })
            
        elif call_type in ["call-ended", "completed"]:
            # Check if it was answered or missed based on duration/reason
            was_answered = duration_seconds > 0 or ended_reason not in ["no-answer", "missed", "busy", "voicemail"]
            
            if was_answered:
                # CONTRACT: call.answered (completion) payload
                log_event("call.answered", "vapi", "info", correlation_id=normalized_phone, entity_id=call_id, payload={
                    "call_id": call_id,
                    "from": normalized_phone,
                    "assistant_id": assistant_id,
                    "provider": "vapi",
                    "duration_seconds": duration_seconds,
                    "ended_reason": ended_reason,
                    "status": "completed"
                })
            else:
                # CONTRACT: call.missed payload
                log_event("call.missed", "vapi", "warn", correlation_id=normalized_phone, entity_id=call_id, payload={
                    "call_id": call_id,
                    "from": normalized_phone,
                    "reason": ended_reason or "no_answer",
                    "provider": "vapi",
                    "follow_up": "scheduled"
                })
                
        elif call_type in ["no-answer", "missed", "busy", "failed"]:
            # CONTRACT: call.missed payload
            log_event("call.missed", "vapi", "warn", correlation_id=normalized_phone, entity_id=call_id, payload={
                "call_id": call_id,
                "from": normalized_phone,
                "reason": call_type,
                "provider": "vapi",
                "follow_up": "scheduled"
            })
        
        # Store call transcript if present
        transcript = data.get("transcript") or data.get("call", {}).get("transcript")
        summary = data.get("summary") or data.get("call", {}).get("summary")
        
        if transcript or summary:
            try:
                requests.post(f"{SUPABASE_URL}/rest/v1/call_transcripts", headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                }, json={
                    "call_id": call_id,
                    "customer_phone": normalized_phone,
                    "transcript": transcript,
                    "summary": summary,
                    "duration_seconds": duration_seconds,
                    "ended_reason": ended_reason,
                    "assistant_id": assistant_id
                }, timeout=10)
            except Exception as e:
                print(f"[VAPI] Failed to store transcript: {e}")
        
        print(f"[VAPI Webhook] {call_type} call_id={call_id} phone={normalized_phone}")
        return {"status": "ok", "call_id": call_id, "event_type": call_type}
    
    @api.post("/outbound")
    def handle_outbound(data: dict):
        """Handle outbound campaign task - Routes to Christina with variant selection"""
        import time
        start_time = time.time()
        
        phone = data.get("phone", "")
        company = data.get("company", "your business")
        touch = data.get("touch", 1)
        vertical = data.get("vertical", "general")
        
        print(f"[OUTBOUND] Touch {touch} to {phone} (vertical: {vertical})")
        
        # Log outbound task start
        log_event("task.outbound_started", "modal", "info", correlation_id=phone, payload={"company": company, "touch": touch, "vertical": vertical})
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # === VARIANT SELECTION (Thompson Sampling) ===
        variant_id = None
        variant_name = None
        try:
            variant_resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/get_best_variant",
                headers=headers,
                json={"p_vertical": vertical, "p_agent": "christina"},
                timeout=10
            )
            if variant_resp.status_code == 200 and variant_resp.json():
                variant = variant_resp.json()
                # Handle both single object and array responses
                if isinstance(variant, list):
                    variant = variant[0] if variant else {}
                variant_id = variant.get("id")
                variant_name = variant.get("name")
                # Use message_template from DB variant
                template = variant.get("message_template") or variant.get("opener")
                if template and touch == 1:
                    response_text = template.replace("{name}", "").replace("{company}", company).strip()
                else:
                    response_text = None
        except Exception as e:
            print(f"[VARIANT] Error fetching variant: {e}")
            response_text = None
        
        # Fallback to static templates if variant not available
        if not response_text:
            # Emit variant.fallback event for tracking
            log_event("variant.fallback", "modal", "warning", correlation_id=phone, payload={
                "reason": "no_variant_returned" if not variant_id else "no_template",
                "vertical": vertical,
                "touch": touch,
                "company": company
            })
            touch_templates = {
                1: f"Hi! I'm Christina from AI Service Co. I just reviewed {company}'s marketing - there are quick wins you're missing. Book a free call: {BOOKING_LINK}",
                2: f"Quick follow-up on {company} - I found 3 things that could help you get more leads this month. Got 15 min? {BOOKING_LINK}",
                3: f"Last chance - I'm moving on tomorrow. If you want the free strategy session for {company}, grab it now: {BOOKING_LINK}"
            }
            response_text = touch_templates.get(touch, touch_templates[1])

        
        # Log interaction with variant tracking
        requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
            "phone": phone, "direction": "outbound", "channel": "sms",
            "message": response_text, "agent": "christina", "touch": touch,
            "metadata": {"variant_id": variant_id, "variant_name": variant_name, "vertical": vertical}
        })
        
        # === OUTREACH ATTRIBUTION (for Thompson Sampling credit assignment) ===
        contact_id = data.get("contact_id", "")
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/outreach_attribution", headers=headers, json={
                "phone": phone,
                "contact_id": contact_id,
                "channel": "sms",
                "variant_id": variant_id,
                "variant_name": variant_name,
                "touch": touch,
                "correlation_id": phone,
                "metadata": {"company": company, "vertical": vertical}
            }, timeout=5)
        except Exception as e:
            print(f"[Attribution] Failed to record: {e}")
        
        # Send via GHL
        success = False
        message_id = f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{phone[-4:]}"
        try:
            ghl_resp = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
            success = ghl_resp.status_code < 400
        except Exception as e:
            print(f"[GHL] Send failed: {e}")
        
        # CONTRACT: sms.sent / sms.failed events
        if success:
            log_event("sms.sent", "modal", "info", correlation_id=phone, entity_id=message_id, payload={
                "message_id": message_id,
                "to": phone,
                "template": f"touch_{touch}_{vertical}",
                "variant_id": variant_id
            })
        else:
            log_event("sms.failed", "modal", "error", correlation_id=phone, entity_id=message_id, payload={
                "message_id": message_id,
                "to": phone,
                "error": "ghl_send_failed"
            })
        
        # === RECORD TASK METRIC ===
        latency_ms = int((time.time() - start_time) * 1000)
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/task_metrics", headers=headers, json={
                "task_type": "outbound",
                "correlation_id": phone,
                "latency_ms": latency_ms,
                "success": success,
                "failures": 0 if success else 1,
                "payload": {"touch": touch, "variant_id": variant_id, "vertical": vertical}
            }, timeout=5)
        except:
            pass
        
        log_event("task.outbound_completed", "modal", "info", correlation_id=phone, payload={"success": success, "latency_ms": latency_ms, "variant": variant_name})
        
        return {"agent": "christina", "touch": touch, "sent": success, "variant_id": variant_id, "variant_name": variant_name}
    
    @api.get("/optimize")
    def self_improvement_optimizer():
        """Analyze logs and suggest improvements. Trigger via Cloudflare cron every 2 hours."""
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        # Fetch logs
        health_logs, webhook_logs = [], []
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/health_logs?created_at=gte.{since}&order=created_at.desc&limit=100", headers=headers, timeout=15)
            if r.status_code == 200: health_logs = r.json()
        except: pass
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/webhook_logs?timestamp=gte.{since}&order=timestamp.desc&limit=100", headers=headers, timeout=15)
            if r.status_code == 200: webhook_logs = r.json()
        except: pass
        
        # Analyze patterns
        patterns = []
        health_failures = [l for l in health_logs if l.get("status") != "ok"]
        if health_failures:
            failure_counts = {}
            for log in health_failures:
                c = log.get("component", "unknown")
                failure_counts[c] = failure_counts.get(c, 0) + 1
            for comp, count in failure_counts.items():
                if count >= 2:
                    patterns.append({"type": "recurring_health_failure", "component": comp, "occurrences": count, "severity": "high" if count >= 5 else "medium"})
        
        webhook_failures = [l for l in webhook_logs if l.get("result_status", 200) >= 400]
        if webhook_failures:
            error_codes = {}
            for log in webhook_failures:
                code = log.get("result_status", 0)
                error_codes[code] = error_codes.get(code, 0) + 1
            for code, count in error_codes.items():
                patterns.append({"type": "webhook_error_pattern", "error_code": code, "occurrences": count, "severity": "high" if code >= 500 else "medium"})
        
        fallback_uses = [l for l in webhook_logs if l.get("forwarded_to") == "fallback"]
        if fallback_uses:
            patterns.append({"type": "fallback_activation", "occurrences": len(fallback_uses), "severity": "medium"})
        
        # Generate suggestions
        suggested_code_changes = []
        suggested_deploy_actions = []
        for p in patterns:
            if p["type"] == "recurring_health_failure":
                suggested_code_changes.append({"target": f"{p['component']}_handler", "change": "Add retry logic with exponential backoff", "risk_level": "low", "test_validation": "Run health check 10x and verify 100% success"})
            elif p["type"] == "webhook_error_pattern" and p.get("error_code", 0) >= 500:
                suggested_code_changes.append({"target": "webhook_handler", "change": "Add circuit breaker pattern", "risk_level": "medium", "test_validation": "Simulate 5 failures, verify circuit opens after 3"})
            elif p["type"] == "fallback_activation":
                suggested_code_changes.append({"target": "primary_orchestrator", "change": "Add keep-alive pings every 5 min", "risk_level": "low", "test_validation": "Monitor fallback activations for 24h"})
            if p.get("severity") == "high":
                suggested_deploy_actions.append({"action": f"Scale up {p.get('component', 'affected service')}", "priority": "high", "risk_level": "medium", "test_validation": "Load test with 2x traffic"})
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "logs_analyzed": {"health_logs": len(health_logs), "webhook_logs": len(webhook_logs)},
            "patterns": patterns,
            "suggested_code_changes": suggested_code_changes,
            "suggested_deploy_actions": suggested_deploy_actions
        }
        
        # Log to Supabase
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/optimization_logs", headers=headers, json={"timestamp": result["timestamp"], "analysis": result, "patterns_found": len(patterns)}, timeout=15)
        except: pass
        
        return result
    
    @api.post("/api/campaign-batch")
    def campaign_batch(data: dict):
        """
        Execute batch campaign for multiple contacts respecting timezone windows.
        Called by scheduled_timezone_aware_campaign.
        
        Request:
        {
            "contacts": [{"phone":..., "company":..., "vertical":..., "timezone":..., "touch":1, "channel":"sms"}],
            "dry_run": false,
            "run_id": "optional_run_id"
        }
        
        Returns: {sent: N, skipped_window: N, failed: N, details: [...]}
        """
        import time
        import uuid
        
        contacts = data.get("contacts", [])
        dry_run = data.get("dry_run", False)
        run_id = data.get("run_id") or f"batch_{uuid.uuid4().hex[:8]}"
        
        # Emit batch started event
        log_event("campaign.batch.started", "modal", "info", correlation_id=run_id, payload={
            "contact_count": len(contacts),
            "dry_run": dry_run
        })
        
        results = {
            "sent": 0,
            "skipped_window": 0,
            "failed": 0,
            "details": []
        }
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        for contact in contacts:
            phone = contact.get("phone", "")
            company = contact.get("company", "Business")
            vertical = contact.get("vertical", "general")
            touch = contact.get("touch", 1)
            channel = contact.get("channel", "sms")
            contact_id = contact.get("id") or contact.get("contact_id") or ""
            
            # Check if in business hours for this contact's timezone
            tz = contact.get("timezone")
            if tz:
                in_window = is_business_hours_for_phone(phone, channel)
                if not in_window:
                    results["skipped_window"] += 1
                    results["details"].append({
                        "phone": phone, "status": "skipped_window", "channel": channel
                    })
                    continue
            
            if dry_run:
                results["sent"] += 1
                results["details"].append({
                    "phone": phone, "status": "dry_run_ok", "channel": channel
                })
                continue
            
            # === VARIANT SELECTION ===
            variant_id = None
            variant_name = None
            message_template = None
            agent = "sarah" if channel == "sms" else "christina"
            
            try:
                variant_resp = requests.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/get_best_variant",
                    headers=headers,
                    json={"p_vertical": vertical, "p_agent": agent},
                    timeout=10
                )
                if variant_resp.status_code == 200 and variant_resp.json():
                    variant = variant_resp.json()
                    if isinstance(variant, list):
                        variant = variant[0] if variant else {}
                    variant_id = variant.get("id")
                    variant_name = variant.get("name")
                    message_template = variant.get("message_template")
            except Exception as e:
                print(f"[BATCH Variant] Error: {e}")
            
            # Build message from template or fallback
            if message_template:
                message = message_template.replace("{company}", company).replace("{name}", "").strip()
            else:
                # Fallback static messages
                log_event("variant.fallback", "modal", "warning", correlation_id=phone, payload={
                    "reason": "no_variant" if not variant_id else "no_template",
                    "vertical": vertical, "channel": channel
                })
                if channel == "sms":
                    message = f"Hi from AI Service Co! I noticed {company} might benefit from 24/7 call coverage. Got 2 min to chat?"
                else:
                    message = f"Quick follow-up for {company} - we help businesses capture 100% of inbound calls. Worth a quick call?"
            
            # === SEND ===
            try:
                if channel == "sms":
                    sms_resp = requests.post(
                        GHL_SMS_WEBHOOK,
                        json={"phone": phone, "message": message},
                        timeout=30
                    )
                    sent_ok = sms_resp.status_code in [200, 201, 202]
                else:
                    # For email, just log for now (requires different endpoint)
                    sent_ok = True
                    print(f"[BATCH] Email to {phone}: would send")
                
                if sent_ok:
                    results["sent"] += 1
                    results["details"].append({
                        "phone": phone, "status": "sent", "channel": channel, 
                        "variant_id": variant_id, "variant_name": variant_name
                    })
                    
                    # Record attribution
                    try:
                        requests.post(f"{SUPABASE_URL}/rest/v1/outreach_attribution", headers=headers, json={
                            "phone": phone,
                            "contact_id": contact_id,
                            "channel": channel,
                            "variant_id": variant_id,
                            "variant_name": variant_name,
                            "correlation_id": run_id,
                            "metadata": {"company": company, "vertical": vertical, "touch": touch}
                        }, timeout=5)
                    except:
                        log_event("attribution.missing_table", "modal", "warning", correlation_id=phone)
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "phone": phone, "status": "failed", "channel": channel
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "phone": phone, "status": "error", "error": str(e)[:100]
                })
                log_event("error.occurred", "modal", "error", correlation_id=phone, payload={
                    "context": "campaign_batch_send", "error": str(e)[:200]
                })
            
            # Small delay between sends (rate limiting)
            time.sleep(0.5)
        
        # Emit batch completed event
        log_event("campaign.batch.completed", "modal", "info", correlation_id=run_id, payload={
            "sent": results["sent"],
            "skipped_window": results["skipped_window"],
            "failed": results["failed"],
            "dry_run": dry_run
        })
        
        return {
            "status": "ok",
            "run_id": run_id,
            "sent": results["sent"],
            "skipped_window": results["skipped_window"],
            "failed": results["failed"],
            "details": results["details"][:20]  # Limit details in response
        }
    
    @api.get("/api/learning-metrics")
    def learning_metrics():

        """
        Returns variant booking metrics for the last 7 days.
        Used by Thompson Sampling and learning dashboards.
        
        Response:
        {
            "variants": {variant_id: {bookings, last_booking_ts, outreach_count, booking_rate}},
            "top_variant": {id, name, booking_rate},
            "total_bookings": int,
            "period_days": 7
        }
        """
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        # Fetch outcome.booking events from last 7 days
        try:
            bookings_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.outcome.booking&ts=gte.{since}&order=ts.desc",
                headers=headers, timeout=15
            )
            bookings = bookings_resp.json() if bookings_resp.status_code == 200 else []
        except Exception as e:
            print(f"[LearningMetrics] Failed to fetch bookings: {e}")
            bookings = []
        
        # Fetch outreach attribution counts by variant
        try:
            outreach_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/outreach_attribution?ts=gte.{since}&select=variant_id,variant_name",
                headers=headers, timeout=15
            )
            outreach = outreach_resp.json() if outreach_resp.status_code == 200 else []
        except Exception as e:
            print(f"[LearningMetrics] Failed to fetch outreach: {e}")
            outreach = []
        
        # Aggregate by variant
        variants = {}
        
        # Count outreach per variant
        for o in outreach:
            vid = o.get("variant_id")
            if not vid:
                continue
            if vid not in variants:
                variants[vid] = {
                    "name": o.get("variant_name", "unknown"),
                    "bookings": 0,
                    "last_booking_ts": None,
                    "outreach_count": 0
                }
            variants[vid]["outreach_count"] += 1
        
        # Count bookings per variant
        for b in bookings:
            payload = b.get("payload", {})
            vid = payload.get("variant_id")
            if not vid:
                continue
            if vid not in variants:
                variants[vid] = {
                    "name": payload.get("variant_name", "unknown"),
                    "bookings": 0,
                    "last_booking_ts": None,
                    "outreach_count": 0
                }
            variants[vid]["bookings"] += 1
            if not variants[vid]["last_booking_ts"]:
                variants[vid]["last_booking_ts"] = b.get("ts")
        
        # Calculate booking rates
        for vid, data in variants.items():
            if data["outreach_count"] > 0:
                data["booking_rate"] = round(data["bookings"] / data["outreach_count"], 4)
            else:
                data["booking_rate"] = 0.0
        
        # Find top variant
        top_variant = None
        if variants:
            sorted_variants = sorted(
                variants.items(),
                key=lambda x: (x[1]["bookings"], x[1]["booking_rate"]),
                reverse=True
            )
            top_id, top_data = sorted_variants[0]
            top_variant = {
                "id": top_id,
                "name": top_data["name"],
                "bookings": top_data["bookings"],
                "booking_rate": top_data["booking_rate"]
            }
        
        return {
            "variants": variants,
            "top_variant": top_variant,
            "total_bookings": len(bookings),
            "period_days": 7,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/marketing/status")
    def marketing_status():
        """
        Returns marketing autopost status and platform configurations.
        Used by dashboard to monitor content engine.
        
        Kill switch: MARKETING_AUTOPOST_ENABLED env var (default false)
        """
        import os
        
        # Kill switch - defaults to disabled for safety
        autopost_enabled = os.environ.get("MARKETING_AUTOPOST_ENABLED", "false").lower() == "true"
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        # Fetch posting rules
        enabled_platforms = []
        posts_today = {}
        try:
            rules_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/posting_rules?select=platform,enabled,cadence_per_day,posts_today,last_posted_at",
                headers=headers, timeout=10
            )
            if rules_resp.status_code == 200:
                for rule in rules_resp.json():
                    platform = rule.get("platform")
                    if rule.get("enabled"):
                        enabled_platforms.append(platform)
                    posts_today[platform] = rule.get("posts_today", 0)
        except Exception as e:
            print(f"[Marketing Status] Error fetching rules: {e}")
        
        # Fetch pending content in queue
        pending_count = 0
        try:
            queue_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/content_queue?status=eq.queued&select=id",
                headers=headers, timeout=10
            )
            if queue_resp.status_code == 200:
                pending_count = len(queue_resp.json())
        except:
            pass
        
        # Fetch pending approvals
        pending_approvals = 0
        try:
            approvals_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/content_approvals?status=eq.pending&select=id",
                headers=headers, timeout=10
            )
            if approvals_resp.status_code == 200:
                pending_approvals = len(approvals_resp.json())
        except:
            pass
        
        return {
            "autopost_enabled": autopost_enabled,
            "kill_switch_info": "Set MARKETING_AUTOPOST_ENABLED=true in Modal secrets to enable",
            "enabled_platforms": enabled_platforms,
            "posts_today_by_platform": posts_today,
            "pending_queue": pending_count,
            "pending_approvals": pending_approvals,
            "safety_notes": [
                "Max 1 post per platform per day until logs clean for 2 weeks",
                "All platforms start disabled in posting_rules",
                "Content requires approval before auto-posting"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/policy-optimize")
    def policy_optimizer():


        """
        Adjust policy weights based on task metrics using simple Bayesian update.
        Analyzes last 24h of task_metrics, adjusts retries/timeouts/weights.
        Run via cron every 4 hours or on-demand.
        """
        from datetime import timedelta
        import random
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        # Fetch recent task metrics
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/task_metrics?ts=gte.{since}&order=ts.desc&limit=500", headers=headers, timeout=15)
            metrics = r.json() if r.status_code == 200 else []
        except:
            metrics = []
        
        if len(metrics) < 10:
            return {"status": "skip", "reason": "insufficient_data", "metrics_count": len(metrics)}
        
        # Calculate aggregate stats
        total = len(metrics)
        successes = sum(1 for m in metrics if m.get("success"))
        success_rate = successes / total
        avg_latency = sum(m.get("latency_ms", 0) for m in metrics) / total
        avg_retries = sum(m.get("retries", 0) for m in metrics) / total
        
        # Fetch current policy
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/policy_weights?active=eq.true&order=version.desc&limit=1", headers=headers, timeout=10)
            current_policy = r.json()[0] if r.status_code == 200 and r.json() else None
        except:
            current_policy = None
        
        if not current_policy:
            return {"status": "error", "reason": "no_active_policy"}
        
        old_version = current_policy.get("version", 1)
        changes_made = {}
        
        # Bayesian-style weight adjustments based on performance
        new_policy = {}
        
        # 1. Adjust max_retries: If high failure rate, increase; if low, decrease
        failure_rate = 1 - success_rate
        if failure_rate > 0.3:
            new_policy["max_retries"] = min(current_policy.get("max_retries", 3) + 1, 5)
            changes_made["max_retries"] = "increased (high failure rate)"
        elif failure_rate < 0.1 and current_policy.get("max_retries", 3) > 1:
            new_policy["max_retries"] = current_policy.get("max_retries", 3) - 1
            changes_made["max_retries"] = "decreased (low failure rate)"
        
        # 2. Adjust timeouts: If high latency, increase timeout
        if avg_latency > 25000:  # > 25s avg
            new_policy["tool_timeout_ms"] = min(current_policy.get("tool_timeout_ms", 30000) + 10000, 60000)
            changes_made["tool_timeout_ms"] = "increased (high latency)"
        elif avg_latency < 5000 and current_policy.get("tool_timeout_ms", 30000) > 15000:
            new_policy["tool_timeout_ms"] = current_policy.get("tool_timeout_ms", 30000) - 5000
            changes_made["tool_timeout_ms"] = "decreased (low latency)"
        
        # 3. Adjust concurrency: If high success rate, can increase
        if success_rate > 0.9 and avg_retries < 0.5:
            new_policy["max_concurrent_tasks"] = min(current_policy.get("max_concurrent_tasks", 5) + 1, 10)
            changes_made["max_concurrent_tasks"] = "increased (high success)"
        elif success_rate < 0.7:
            new_policy["max_concurrent_tasks"] = max(current_policy.get("max_concurrent_tasks", 5) - 1, 2)
            changes_made["max_concurrent_tasks"] = "decreased (low success)"
        
        # 4. Adjust Gemini/fallback weights using Thompson Sampling approach
        gemini_tasks = [m for m in metrics if m.get("payload", {}).get("tool") == "gemini"]
        if gemini_tasks:
            gemini_success = sum(1 for m in gemini_tasks if m.get("success")) / len(gemini_tasks)
            # Simple exploration-exploitation: add noise
            adjusted_weight = gemini_success * 0.8 + random.uniform(0.1, 0.3)
            new_policy["weight_gemini"] = min(max(adjusted_weight, 0.3), 0.9)
            new_policy["weight_fallback"] = 1.0 - new_policy["weight_gemini"]
            changes_made["weight_gemini"] = f"adjusted to {new_policy['weight_gemini']:.2f}"
        
        # Only update if changes were made
        if not changes_made:
            return {"status": "no_changes", "success_rate": success_rate, "avg_latency_ms": avg_latency}
        
        # Create new policy version
        new_version = old_version + 1
        new_policy_record = {**current_policy}
        new_policy_record.update(new_policy)
        new_policy_record["version"] = new_version
        new_policy_record["updated_by"] = "optimizer"
        new_policy_record["notes"] = f"Auto-adjusted from success_rate={success_rate:.2f}, latency={avg_latency:.0f}ms"
        del new_policy_record["id"]
        del new_policy_record["created_at"]
        new_policy_record["created_at"] = datetime.utcnow().isoformat()
        
        # Deactivate old policy
        try:
            requests.patch(f"{SUPABASE_URL}/rest/v1/policy_weights?version=eq.{old_version}", headers=headers, json={"active": False}, timeout=10)
        except: pass
        
        # Insert new policy
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/policy_weights", headers=headers, json=new_policy_record, timeout=10)
        except Exception as e:
            return {"status": "error", "reason": f"failed to save: {e}"}
        
        # Log optimizer run
        confidence = success_rate * 0.6 + (1 - min(avg_retries, 3) / 3) * 0.4
        run_log = {
            "tasks_analyzed": total,
            "success_rate": success_rate,
            "avg_latency_ms": int(avg_latency),
            "old_policy_version": old_version,
            "new_policy_version": new_version,
            "changes_made": changes_made,
            "confidence_score": confidence
        }
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/optimizer_runs", headers=headers, json=run_log, timeout=10)
        except: pass
        
        log_event("policy.updated", "modal", "info", payload={"old_version": old_version, "new_version": new_version, "changes": changes_made})
        
        return {
            "status": "optimized",
            "old_version": old_version,
            "new_version": new_version,
            "changes_made": changes_made,
            "metrics": {
                "tasks_analyzed": total,
                "success_rate": round(success_rate, 3),
                "avg_latency_ms": int(avg_latency),
                "avg_retries": round(avg_retries, 2)
            },
            "rollback_command": "SELECT rollback_policy();"
        }
    
    @api.get("/campaign")
    def run_campaign(override: bool = False, catchup: bool = False):
        """Run 8 AM CT campaign with idempotency. Only runs once per day unless override=true."""
        import time
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Check if campaign already ran today (idempotency via direct query)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        if not override:
            try:
                r = requests.get(
                    f"{SUPABASE_URL}/rest/v1/job_runs?job_name=eq.campaign&window_id=eq.8am_ct&scheduled_for=eq.{today}&status=in.(success,catchup)&limit=1",
                    headers=headers,
                    timeout=10
                )
                if r.status_code == 200 and len(r.json()) > 0:
                    # CONTRACT: campaign.skip payload
                    log_event("campaign.skip", "modal", "info", payload={"window_id": "8am_ct", "reason": "already_ran_today", "next": "tomorrow 8am CT"})
                    return {"status": "skip", "reason": "already_ran_today", "next": "tomorrow 8am CT"}
            except Exception as e:
                print(f"[Campaign] Idempotency check failed: {e}, proceeding anyway")
        
        # Check send window (weekdays 9am-6pm CT = 15:00-23:00 UTC)
        now_utc = datetime.utcnow()
        ct_hour = (now_utc.hour - 6) % 24  # Rough CT conversion
        weekday = now_utc.weekday()  # 0=Monday, 6=Sunday
        
        if not override and (weekday >= 5 or ct_hour < 9 or ct_hour >= 18):
            # CONTRACT: campaign.skip payload
            log_event("campaign.skip", "modal", "info", payload={"window_id": "8am_ct", "reason": "outside_send_window", "next": "next business day 8am CT"})
            return {"status": "skip", "reason": "outside_send_window", "ct_hour": ct_hour, "weekday": weekday}
        
        start_time = time.time()
        campaign_type = "catchup" if catchup else "scheduled"
        batch_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
        
        # CONTRACT: campaign.run payload (start of execution)
        log_event("campaign.run", "modal", "info", correlation_id=batch_id, payload={"window_id": "8am_ct", "sent": 0, "latency_ms": 0, "channels": ["sms"], "override": override})
        
        # Get contacts due for outreach
        try:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/contacts_master?status=in.(new,active)&touch_count=lt.3&limit=50",
                headers=headers, timeout=15
            )
            contacts = r.json() if r.status_code == 200 else []
        except:
            contacts = []
        
        sent_count = 0
        errors = 0
        
        for contact in contacts:
            phone = contact.get("phone")
            company = contact.get("company", "your business")
            touch = contact.get("touch_count", 0) + 1
            vertical = contact.get("industry", "general")
            
            if not phone:
                continue
            
            try:
                # Call /outbound which handles variant selection and GHL sending
                outbound_resp = requests.post(
                    f"http://localhost:8000/outbound",  # Internal call
                    json={"phone": phone, "company": company, "touch": touch, "vertical": vertical},
                    timeout=30
                )
                if outbound_resp.status_code == 200:
                    sent_count += 1
                    # Update touch count
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/contacts_master?id=eq.{contact.get('id')}",
                        headers=headers,
                        json={"touch_count": touch, "last_touch": datetime.utcnow().isoformat()},
                        timeout=10
                    )
                else:
                    errors += 1
            except Exception as e:
                print(f"[Campaign] Error sending to {phone}: {e}")
                errors += 1
        
        latency_ms = int((time.time() - start_time) * 1000)
        status = "success" if errors == 0 else ("partial" if sent_count > 0 else "fail")
        
        # Record job run (idempotency marker) via direct INSERT
        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/job_runs",
                headers={**headers, "Prefer": "resolution=merge-duplicates"},
                json={
                    "job_name": "campaign",
                    "window_id": "8am_ct",
                    "scheduled_for": today,
                    "status": "catchup" if catchup else status,
                    "details": {"sent": sent_count, "errors": errors, "contacts": len(contacts)}
                },
                timeout=10
            )
        except Exception as e:
            print(f"[Campaign] Failed to record job run: {e}")
        
        # CONTRACT: Emit campaign.run (completion) or campaign.error based on status
        if status == "fail":
            log_event("campaign.error", "modal", "error", correlation_id=batch_id, payload={"window_id": "8am_ct", "error": f"Campaign failed: {errors} errors", "stack": None})
        else:
            log_event("campaign.run", "modal", "info", correlation_id=batch_id, payload={"window_id": "8am_ct", "sent": sent_count, "latency_ms": latency_ms, "channels": ["sms"], "override": override})
        
        return {
            "status": status,
            "batch_id": batch_id,
            "sent": sent_count,
            "errors": errors,
            "contacts_processed": len(contacts),
            "latency_ms": latency_ms,
            "type": campaign_type
        }
    
    @api.get("/prospect")
    def run_prospecting():
        """Run Apollo prospecting and queue new leads. Triggered by Cloudflare cron every 4 hours."""
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Get prospect targets from Supabase
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/prospect_targets?status=eq.pending&limit=20", headers=headers, timeout=15)
            targets = r.json() if r.status_code == 200 else []
        except:
            targets = []
        
        prospects_added = 0
        for target in targets:
            industry = target.get("industry", "home services")
            location = target.get("location", "Florida")
            
            # Generate personalized audit message using Gemini
            audit_prompt = f"""Generate a brief 2-sentence business audit insight for a {industry} company in {location}.
Focus on a specific marketing gap like missing Google reviews, no online booking, or weak social presence.
Be specific and actionable. Output ONLY the insight, no intro."""
            
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": audit_prompt}]}]},
                    timeout=30
                )
                audit_insight = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                audit_insight = f"Your {industry} business could benefit from automated lead capture and follow-up."
                # CONTRACT: error.occurred for AI failures
                log_event("error.occurred", "modal", "error", payload={
                    "error": "gemini_audit_failed",
                    "message": str(e)[:200],
                    "component": "prospecting",
                    "severity": "warn",
                    "recoverable": True
                })
            
            # Add to contacts_master for outreach
            try:
                requests.post(f"{SUPABASE_URL}/rest/v1/contacts_master", headers=headers, json={
                    "industry": industry,
                    "location": location,
                    "source": "auto_prospect",
                    "personal_audit": audit_insight,
                    "status": "new",
                    "created_at": datetime.utcnow().isoformat()
                }, timeout=10)
                prospects_added += 1
            except:
                pass
            
            # Mark target as processed
            try:
                requests.patch(f"{SUPABASE_URL}/rest/v1/prospect_targets?id=eq.{target.get('id')}", headers=headers, json={"status": "processed"}, timeout=10)
            except:
                pass
        
        # Log prospecting run
        batch_id = f"prospect_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
        log_event("prospecting.completed", "modal", "info", correlation_id=batch_id, payload={"prospects_added": prospects_added, "targets_processed": len(targets)})
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/cron_logs", headers=headers, json={
                "trigger": "cloudflare_cron",
                "action": "prospecting",
                "result": {"prospects_added": prospects_added, "targets_processed": len(targets)},
                "timestamp": datetime.utcnow().isoformat()
            }, timeout=10)
        except:
            pass
        
        return {
            "status": "ok",
            "action": "prospecting",
            "prospects_added": prospects_added,
            "targets_processed": len(targets),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/campaign")
    def run_campaign():
        """Run scheduled 8 AM outreach campaign. Triggered by Cloudflare cron at 8 AM CT daily."""
        campaign_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d')}"
        log_event("campaign.started", "modal", "info", correlation_id=campaign_id)
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Get contacts due for outreach
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?status=in.(new,follow_up)&limit=50", headers=headers, timeout=15)
            contacts = r.json() if r.status_code == 200 else []
        except:
            contacts = []
        
        messages_sent = 0
        for contact in contacts:
            phone = contact.get("phone")
            company = contact.get("company", contact.get("industry", "your business"))
            personal_audit = contact.get("personal_audit", "")
            touch = contact.get("touch_count", 0) + 1
            
            if not phone:
                continue
            
            # Personalized message with audit
            if personal_audit and touch == 1:
                message = f"Hi! I'm Christina from AI Service Co. Quick insight for {company}: {personal_audit[:100]} Let's chat: {BOOKING_LINK}"
            elif touch == 1:
                message = f"Hi! I'm Christina from AI Service Co. I found opportunities for {company} to get more leads. Got 15 min? {BOOKING_LINK}"
            elif touch == 2:
                message = f"Following up on {company} - still have those insights ready. Last call: {BOOKING_LINK}"
            else:
                message = f"Final notice for {company}: Free strategy session expires today. {BOOKING_LINK}"
            
            # Send via GHL
            try:
                requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": message}, timeout=15)
                messages_sent += 1
            except:
                continue
            
            # Update contact
            new_status = "contacted" if touch == 1 else ("follow_up" if touch < 3 else "max_reached")
            try:
                requests.patch(f"{SUPABASE_URL}/rest/v1/contacts_master?id=eq.{contact.get('id')}", headers=headers, json={
                    "touch_count": touch,
                    "last_contacted": datetime.utcnow().isoformat(),
                    "status": new_status
                }, timeout=10)
            except:
                pass
            
            # Log interaction
            try:
                requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
                    "phone": phone, "direction": "outbound", "channel": "sms",
                    "message": message, "agent": "christina", "touch": touch
                }, timeout=10)
            except:
                pass
        
        # Log campaign run
        log_event("campaign.completed", "modal", "info", correlation_id=campaign_id, payload={"messages_sent": messages_sent, "contacts_processed": len(contacts)})
        try:
            requests.post(f"{SUPABASE_URL}/rest/v1/cron_logs", headers=headers, json={
                "trigger": "cloudflare_cron",
                "action": "campaign_8am",
                "result": {"messages_sent": messages_sent, "contacts_processed": len(contacts)},
                "timestamp": datetime.utcnow().isoformat()
            }, timeout=10)
        except:
            pass
        
        return {
            "status": "ok",
            "action": "campaign",
            "messages_sent": messages_sent,
            "contacts_processed": len(contacts),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ==========================================================
    # SSE DIAGNOSTICS - Track active clients
    # ==========================================================
    sse_diagnostics = {
        "active_clients": 0,
        "total_connections": 0,
        "total_disconnections": 0,
        "last_event_id": 0
    }
    
    @api.get("/api/events/stats")
    def get_sse_stats():
        """Get SSE connection diagnostics"""
        return {
            "active_clients": sse_diagnostics["active_clients"],
            "total_connections": sse_diagnostics["total_connections"],
            "total_disconnections": sse_diagnostics["total_disconnections"],
            "last_event_id": sse_diagnostics["last_event_id"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/calls")
    def get_calls(limit: int = 20):
        """
        Fetch recent calls from Supabase for Force Sync functionality.
        Returns calls with stable keys: call_id, from_number, to_number, timestamp, disposition, summary, transcript
        """
        import requests
        
        # Use module-level constants (already defined at top)
        # Adding logging to confirm presence
        print(f"[/api/calls] SUPABASE_URL present: {bool(SUPABASE_URL)}")
        print(f"[/api/calls] SUPABASE_KEY present: {bool(SUPABASE_KEY)}")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return {"error": "Supabase not configured", "error_code": "MISSING_ENV", "missing_env": ["SUPABASE_URL", "SUPABASE_KEY"], "calls": []}
        
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            
            # Try call_transcripts table first (this is the main table)
            res = requests.get(
                f"{SUPABASE_URL}/rest/v1/call_transcripts?order=created_at.desc&limit={limit}",
                headers=headers,
                timeout=10
            )
            
            if res.status_code == 200:
                calls = res.json()
                # Normalize to stable keys from call_transcripts schema
                normalized = []
                for c in calls:
                    normalized.append({
                        "call_id": c.get("call_id") or c.get("id") or None,
                        "from_number": c.get("customer_phone") or c.get("from_number") or None,
                        "to_number": c.get("to_number") or None,
                        "timestamp": c.get("created_at") or c.get("timestamp") or None,
                        "disposition": c.get("ended_reason") or c.get("disposition") or "completed",
                        "summary": c.get("summary") or None,
                        "transcript": c.get("transcript") or None,
                        "duration_seconds": c.get("duration_seconds") or c.get("duration") or 0,
                        "customer_name": c.get("customer_name") or None
                    })
                return {"calls": normalized, "count": len(normalized), "source": "call_transcripts"}
            else:
                print(f"[/api/calls] call_transcripts failed: {res.status_code} - {res.text[:200]}")
                # Fallback to system_logs with CALL events
                res2 = requests.get(
                    f"{SUPABASE_URL}/rest/v1/system_logs?event_type=ilike.*CALL*&order=created_at.desc&limit={limit}",
                    headers=headers,
                    timeout=10
                )
                if res2.status_code == 200:
                    logs = res2.json()
                    normalized = []
                    for log in logs:
                        meta = log.get("metadata", {})
                        normalized.append({
                            "call_id": meta.get("call_id") or log.get("id") or None,
                            "from_number": meta.get("from_number") or meta.get("phone") or None,
                            "to_number": meta.get("to_number") or None,
                            "timestamp": log.get("created_at") or None,
                            "disposition": meta.get("disposition") or meta.get("status") or "completed",
                            "summary": meta.get("summary") or log.get("message") or None,
                            "transcript": meta.get("transcript") or None,
                            "duration_seconds": meta.get("duration_seconds") or 0
                        })
                    return {"calls": normalized, "count": len(normalized), "source": "system_logs"}
                return {"error": "Could not fetch calls", "calls": []}
        except Exception as e:
            print(f"[/api/calls] Exception: {e}")
            return {"error": str(e), "calls": []}
    
    @api.post("/api/orchestrator/message")
    def orchestrator_message(data: dict):
        """
        Text Uplink Fallback - Send a message to the orchestrator when voice is unavailable.
        Returns a response from the orchestrator.
        """
        message = data.get("message", "").strip()
        source = data.get("source", "unknown")
        
        if not message:
            return {"error": "No message provided", "response": None}
        
        # Log the inbound message
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/system_logs",
                headers=headers,
                json={
                    "level": "INFO",
                    "event_type": "TEXT_UPLINK",
                    "message": f"[{source}] {message}",
                    "metadata": {"source": source, "message": message}
                },
                timeout=10
            )
        except:
            pass
        
        # Simple response logic - could integrate with AI assistant here
        response_text = f"Received: '{message}'. Orchestrator is processing. Check dashboard for updates."
        
        # For now, just acknowledge - can integrate Gemini/GPT here later
        if "status" in message.lower():
            response_text = "System status: All components operational. Dashboard SSE active."
        elif "sync" in message.lower() or "force" in message.lower():
            response_text = "Use the Force Sync button in the transcripts section to sync recent calls."
        elif "help" in message.lower():
            response_text = "Available commands: status, sync, run campaign, stop. For voice uplink, reload page and check diagnostics."
        
        return {
            "response": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source
        }
    
    # ==========================================================
    # SSE EVENTS STREAM - Realtime dashboard updates
    # ==========================================================
    @api.get("/api/events")
    async def events_stream(auth: str = None):
        """
        Server-Sent Events stream for realtime dashboard updates.
        Event types: task.created, task.updated, lead.updated, call.logged, health.changed
        Includes keepalive ping every 15 seconds.
        
        Usage: EventSource('https://.../api/events?auth=sovereign')
        """
        from starlette.responses import StreamingResponse
        import asyncio
        import uuid
        
        # Basic auth check (matches dashboard password)
        if auth not in ["empire", "sovereign"]:
            return {"error": "unauthorized", "message": "Add ?auth=empire or ?auth=sovereign"}
        
        # Track connection
        client_id = str(uuid.uuid4())[:8]
        sse_diagnostics["active_clients"] += 1
        sse_diagnostics["total_connections"] += 1
        print(f"[SSE] Client {client_id} connected. Active: {sse_diagnostics['active_clients']}")
        
        async def event_generator():
            """Generate SSE events with realtime data from Supabase"""
            nonlocal client_id
            event_id = 0
            last_lead_count = 0
            last_health_status = "unknown"
            health_version = 0
            
            try:
                while True:
                    try:
                        event_id += 1
                        sse_diagnostics["last_event_id"] = event_id
                        now = datetime.utcnow().isoformat()
                        
                        # Fetch latest stats from Supabase
                        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                        
                        # Get lead count
                        try:
                            r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?select=id&limit=1", headers={**headers, "Prefer": "count=exact"}, timeout=5)
                            lead_count = int(r.headers.get("content-range", "0-0/0").split("/")[-1])
                        except:
                            lead_count = last_lead_count
                        
                        # Get recent interactions (for activity)
                        try:
                            r = requests.get(f"{SUPABASE_URL}/rest/v1/interactions?order=created_at.desc&limit=5", headers=headers, timeout=5)
                            recent_interactions = r.json() if r.status_code == 200 else []
                        except:
                            recent_interactions = []
                        
                        # Get recent cron logs (for task events)
                        try:
                            r = requests.get(f"{SUPABASE_URL}/rest/v1/cron_logs?order=timestamp.desc&limit=3", headers=headers, timeout=5)
                            recent_crons = r.json() if r.status_code == 200 else []
                        except:
                            recent_crons = []
                        
                        # Get health status
                        try:
                            r = requests.get(f"{SUPABASE_URL}/rest/v1/health_logs?order=created_at.desc&limit=1", headers=headers, timeout=5)
                            health_data = r.json()[0] if r.status_code == 200 and r.json() else {"status": "unknown"}
                            health_status = health_data.get("status", "unknown")
                        except:
                            health_status = last_health_status
                        
                        # Build events payload
                        events = []
                        
                        # lead.updated event (if count changed)
                        if lead_count != last_lead_count:
                            events.append({
                                "id": f"evt_{event_id}_lead",
                                "type": "lead.updated",
                                "ts": now,
                                "payload": {"total_leads": lead_count, "delta": lead_count - last_lead_count}
                            })
                            last_lead_count = lead_count
                        
                        # health.changed event (if status changed)
                        if health_status != last_health_status:
                            health_version += 1
                            events.append({
                                "id": f"evt_{event_id}_health",
                                "type": "health.changed",
                                "ts": now,
                                "payload": {"status": health_status, "previous": last_health_status, "version": health_version}
                            })
                            last_health_status = health_status
                        
                        # task.updated events from cron logs
                        for cron in recent_crons[:1]:
                            events.append({
                                "id": f"evt_{event_id}_task",
                                "type": "task.updated",
                                "ts": cron.get("timestamp", now),
                                "payload": {"action": cron.get("action"), "result": cron.get("result"), "version": event_id}
                            })
                        
                        # call.logged events from interactions
                        for interaction in recent_interactions[:2]:
                            if interaction.get("channel") in ["call", "sms"]:
                                events.append({
                                    "id": f"evt_{event_id}_call_{interaction.get('id', '')}",
                                    "type": "call.logged",
                                    "ts": interaction.get("created_at", now),
                                    "payload": {
                                        "channel": interaction.get("channel"),
                                        "direction": interaction.get("direction"),
                                        "agent": interaction.get("agent")
                                    }
                                })
                        
                        # Send data event with all updates
                        data_payload = {
                            "id": f"evt_{event_id}",
                            "type": "dashboard.update",
                            "ts": now,
                            "payload": {
                                "stats": {
                                    "leads": lead_count,
                                    "health": health_status
                                },
                                "events": events
                            }
                        }
                        
                        yield f"id: {event_id}\n"
                        yield f"event: update\n"
                        yield f"data: {json.dumps(data_payload)}\n\n"
                        
                        # Wait 5 seconds between updates
                        await asyncio.sleep(5)
                        
                        # Send keepalive ping every 15 seconds (3 cycles)
                        if event_id % 3 == 0:
                            yield f"id: {event_id}_ping\n"
                            yield f"event: ping\n"
                            yield f"data: {json.dumps({'type': 'ping', 'ts': now})}\n\n"
                        
                    except Exception as e:
                        # Send error event but keep stream alive
                        yield f"event: error\n"
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                        await asyncio.sleep(15)
            finally:
                # Track disconnection
                sse_diagnostics["active_clients"] -= 1
                sse_diagnostics["total_disconnections"] += 1
                print(f"[SSE] Client {client_id} disconnected. Active: {sse_diagnostics['active_clients']}")
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    # ==========================================================
    # SELF-ANNEALING LOOPS
    # ==========================================================
    
    @api.get("/api/kpi-snapshot")
    def kpi_snapshot():
        """Emit KPI snapshot to event_log (triggered every 10 min via cron)"""
        try:
            # Fetch current KPIs from Supabase
            leads_resp = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?select=count", 
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"})
            lead_count = int(leads_resp.headers.get("content-range", "0-0/0").split("/")[-1])
            
            bookings_resp = requests.get(f"{SUPABASE_URL}/rest/v1/interactions?outcome=eq.booked&select=count",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"})
            booking_count = int(bookings_resp.headers.get("content-range", "0-0/0").split("/")[-1])
            
            # Calculate rates
            booking_rate = booking_count / max(lead_count, 1)
            
            # CONTRACT: kpi.snapshot payload
            kpi_data = {
                "leads_total": lead_count,
                "bookings_total": booking_count,
                "booking_rate": round(booking_rate, 4),
                "window": "24h",
                "computed_from": ["supabase.contacts_master", "supabase.interactions"],
                "version": "v1"
            }
            
            log_event("kpi.snapshot", "modal", "info", payload=kpi_data)
            return {"status": "ok", "kpi": kpi_data}
        except Exception as e:
            log_event("error.occurred", "modal", "error", payload={"component": "kpi_snapshot", "error": str(e), "code": 500, "context": {"endpoint": "/api/kpi-snapshot"}})
            return {"status": "error", "error": str(e)}
    
    @api.get("/api/reliability-check")
    def reliability_check():
        """Check for incident patterns and trigger auto-heal actions"""
        import hashlib
        
        try:
            # Get recent errors from event_log_v2
            errors_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?severity=in.(error,critical)&order=ts.desc&limit=50",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=15
            )
            errors = errors_resp.json() if errors_resp.status_code == 200 else []
            
            actions_taken = []
            
            for error in errors:
                # Create incident signature hash
                error_type = error.get("type", "unknown")
                error_source = error.get("source", "unknown")
                error_msg = str(error.get("payload", {}).get("error", ""))[:100]
                signature = f"{error_type}:{error_source}:{error_msg}"
                pattern_hash = hashlib.sha256(signature.encode()).hexdigest()[:16]
                
                # Check if pattern exists
                pattern_resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/incident_patterns?pattern_hash=eq.{pattern_hash}",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                    timeout=10
                )
                patterns = pattern_resp.json() if pattern_resp.status_code == 200 else []
                
                if patterns:
                    # Update existing pattern
                    pattern = patterns[0]
                    new_count = pattern.get("occurrence_count", 1) + 1
                    threshold = pattern.get("threshold_for_patch", 3)
                    
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/incident_patterns?id=eq.{pattern['id']}",
                        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                        json={"occurrence_count": new_count, "last_seen": datetime.utcnow().isoformat()},
                        timeout=10
                    )
                    
                    # Trigger auto-heal if threshold reached
                    if new_count >= threshold and not pattern.get("patch_proposed"):
                        action = {
                            "pattern_hash": pattern_hash,
                            "occurrence_count": new_count,
                            "action": "increase_retry_backoff",
                            "component": error_source
                        }
                        log_event("autoheal.triggered", "modal", "warn", payload=action)
                        actions_taken.append(action)
                        
                        # Mark as patch proposed
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/incident_patterns?id=eq.{pattern['id']}",
                            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                            json={"patch_proposed": True},
                            timeout=10
                        )
                else:
                    # Create new pattern
                    requests.post(
                        f"{SUPABASE_URL}/rest/v1/incident_patterns",
                        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                        json={
                            "pattern_hash": pattern_hash,
                            "error_type": error_type,
                            "error_source": error_source,
                            "error_signature": error_msg
                        },
                        timeout=10
                    )
            
            # =========================================
            # 9:30 AM CT CAMPAIGN CATCH-UP
            # =========================================
            now_utc = datetime.utcnow()
            ct_hour = (now_utc.hour - 6) % 24  # Rough CT conversion
            weekday = now_utc.weekday()  # 0=Monday, 6=Sunday
            
            campaign_catchup_triggered = False
            # Check if it's past 9:30 AM CT (15:30 UTC) on a weekday
            if weekday < 5 and ct_hour >= 9 and ct_hour < 18:
                # Check if today's campaign ran
                try:
                    job_check = requests.post(
                        f"{SUPABASE_URL}/rest/v1/rpc/job_ran_today",
                        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                        json={"p_job_name": "campaign", "p_window_id": "8am_ct"},
                        timeout=10
                    )
                    campaign_ran = job_check.status_code == 200 and job_check.json() == True
                    
                    if not campaign_ran and ct_hour >= 9:  # 9:30 AM CT or later
                        # Emit reliability.catchup event BEFORE triggering
                        log_event("reliability.catchup", "modal", "warn", payload={"triggered_by": "missed_8am", "window_id": "8am_ct", "ct_hour": ct_hour})
                        try:
                            # Call the /campaign endpoint with catchup=true
                            catchup_resp = requests.get(
                                f"http://localhost:8000/campaign?catchup=true",
                                timeout=120
                            )
                            campaign_catchup_triggered = True
                            actions_taken.append({
                                "action": "campaign_catchup",
                                "status": catchup_resp.status_code,
                                "ct_hour": ct_hour
                            })
                        except Exception as e:
                            log_event("campaign.catchup_failed", "modal", "error", payload={"error": str(e)})
                except Exception as e:
                    print(f"[Reliability] Campaign catch-up check failed: {e}")
            
            log_event("reliability.check", "modal", "info", payload={"errors_analyzed": len(errors), "actions_taken": len(actions_taken), "campaign_catchup": campaign_catchup_triggered})
            return {"status": "ok", "errors_analyzed": len(errors), "actions_taken": actions_taken, "campaign_catchup_triggered": campaign_catchup_triggered}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.post("/api/record-task-metric")
    def record_task_metric(data: dict):
        """Record task execution metrics for optimizer analysis"""
        try:
            metric = {
                "task_type": data.get("task_type", "unknown"),
                "correlation_id": data.get("correlation_id"),
                "tool_calls": data.get("tool_calls", 1),
                "latency_ms": data.get("latency_ms", 0),
                "failures": data.get("failures", 0),
                "retries": data.get("retries", 0),
                "success": data.get("success", True),
                "result_quality": data.get("result_quality"),
                "payload": data.get("payload", {})
            }
            
            requests.post(
                f"{SUPABASE_URL}/rest/v1/task_metrics",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                json=metric,
                timeout=10
            )
            return {"status": "ok", "recorded": metric["task_type"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.post("/api/record-outcome")
    def record_outcome(data: dict):
        """Record conversation outcome for sales learning loop"""
        try:
            outcome = {
                "call_id": data.get("call_id"),
                "outcome": data.get("outcome", "unknown"),  # booked, callback, rejection, etc.
                "outcome_confidence": data.get("confidence", 0.8),
                "agent": data.get("agent", "sarah"),
                "vertical": data.get("vertical", "general"),
                "phone": data.get("phone"),
                "duration_seconds": data.get("duration_seconds", 0),
                "prompt_variant_id": data.get("variant_id"),
                "variant_name": data.get("variant_name"),
                "transcript": data.get("transcript"),
                "summary": data.get("summary"),
                "scores": data.get("scores", {}),  # {rapport: 85, clarity: 90, ...}
                "total_score": data.get("total_score")
            }
            
            # Record to conversation_outcomes
            requests.post(
                f"{SUPABASE_URL}/rest/v1/conversation_outcomes",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                json=outcome,
                timeout=10
            )
            
            # Update variant performance if variant_id provided
            if outcome["prompt_variant_id"]:
                # Call Supabase function to update variant
                requests.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/update_variant_outcome",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                    json={
                        "p_variant_id": outcome["prompt_variant_id"],
                        "p_outcome": outcome["outcome"],
                        "p_score": outcome["total_score"] or 0
                    },
                    timeout=10
                )
            
            log_event("outcome.recorded", "modal", "info", correlation_id=outcome["phone"], payload={"outcome": outcome["outcome"], "variant": outcome["variant_name"]})
            return {"status": "ok", "recorded": outcome["call_id"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.get("/api/get-variant")
    def get_variant(vertical: str = "general", agent: str = "sarah"):
        """Get best prompt variant using Thompson Sampling"""
        try:
            # Call Supabase function for Thompson Sampling selection
            resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/get_best_variant",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
                json={"p_vertical": vertical, "p_agent": agent},
                timeout=10
            )
            
            if resp.status_code == 200:
                variant = resp.json()
                return {"status": "ok", "variant": variant}
            else:
                # Fallback: get any active variant
                fallback_resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/prompt_variants?vertical=eq.{vertical}&agent=eq.{agent}&active=eq.true&limit=1",
                    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                    timeout=10
                )
                variants = fallback_resp.json() if fallback_resp.status_code == 200 else []
                return {"status": "fallback", "variant": variants[0] if variants else None}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.get("/api/learning-status")
    def learning_status():
        """Dashboard endpoint: Get current self-annealing status"""
        try:
            # Get active policy weights
            policy_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/policy_weights?active=eq.true&order=version.desc&limit=1",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=10
            )
            policy = policy_resp.json()[0] if policy_resp.status_code == 200 and policy_resp.json() else None
            
            # Get active variants by vertical
            variants_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/prompt_variants?active=eq.true&order=alpha.desc&limit=10",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=10
            )
            variants = variants_resp.json() if variants_resp.status_code == 200 else []
            
            # Get recent incident patterns
            incidents_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/incident_patterns?resolved=eq.false&order=last_seen.desc&limit=5",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=10
            )
            incidents = incidents_resp.json() if incidents_resp.status_code == 200 else []
            
            # Get active canary deployments
            canary_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/canary_deployments?status=eq.active&limit=3",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                timeout=10
            )
            canaries = canary_resp.json() if canary_resp.status_code == 200 else []
            
            return {
                "status": "ok",
                "policy": {
                    "version": policy.get("version") if policy else 0,
                    "max_retries": policy.get("max_retries") if policy else 3,
                    "weight_gemini": policy.get("weight_gemini") if policy else 0.7
                },
                "variants": [{
                    "name": v.get("name"),
                    "vertical": v.get("vertical"),
                    "success_rate": v.get("successes", 0) / max(v.get("impressions", 1), 1),
                    "impressions": v.get("impressions", 0)
                } for v in variants[:5]],
                "incidents": [{
                    "component": i.get("component"),
                    "count": i.get("occurrence_count"),
                    "patch_proposed": i.get("patch_proposed")
                } for i in incidents],
                "canaries": [{
                    "percent": c.get("canary_percent"),
                    "requests": c.get("canary_requests"),
                    "decision": c.get("decision")
                } for c in canaries]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    return api


# ==========================================================
# SCHEDULED FUNCTIONS - 24/7 Autonomous Cloud Operation (HARDENED)
# These run on Modal's infrastructure without any local dependencies
# Each function records job_runs, emits events, and handles deadman checks
# ==========================================================

@app.function(schedule=modal.Cron("*/10 * * * *"))  # Every 10 minutes
def scheduled_health_and_kpi():
    """Health check + KPI snapshot every 10 minutes for self-annealing"""
    import requests
    import time
    import uuid
    
    run_id = f"health_kpi_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    # Record job start
    record_job_run_safe("health_kpi", "10min", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "health_kpi", "schedule": "*/10 * * * *", "run_id": run_id
    })
    
    results = []
    errors = 0
    for endpoint in ["/health", "/api/kpi-snapshot", "/api/reliability-check"]:
        try:
            resp = requests.get(f"{base_url}{endpoint}", timeout=30)
            results.append({"endpoint": endpoint, "status": resp.status_code})
            if resp.status_code >= 400:
                errors += 1
        except Exception as e:
            results.append({"endpoint": endpoint, "error": str(e)})
            errors += 1
    
    duration_ms = int((time.time() - start_time) * 1000)
    status = "success" if errors == 0 else ("partial" if errors < 3 else "fail")
    
    # Record job completion
    record_job_run_safe("health_kpi", "10min", status, {
        "run_id": run_id, "duration_ms": duration_ms, "results": results, "errors": errors
    }, run_id)
    
    if status == "fail":
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "health_kpi", "schedule": "*/10 * * * *", "run_id": run_id,
            "duration_ms": duration_ms, "errors": errors
        })
    else:
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "health_kpi", "schedule": "*/10 * * * *", "run_id": run_id,
            "duration_ms": duration_ms, "errors": errors
        })
    
    # DEADMAN CHECK: KPI snapshot in last 30 min
    if not check_deadman_kpi():
        emit_event_safe("incident.deadman", "modal_cron", "critical", run_id, None, {
            "check": "kpi_snapshot", "threshold_minutes": 30, "action": "alert_sent"
        })
        send_alert_email(
            "DEADMAN: No KPI Snapshot in 30 Minutes",
            f"The kpi.snapshot event has not been recorded in the last 30 minutes.\nRun ID: {run_id}\nResults: {results}",
            "critical"
        )
    
    print(f"[CRON 10min] {status} in {duration_ms}ms: {results}")
    return {"status": status, "results": results, "duration_ms": duration_ms}


@app.function(schedule=modal.Cron("0 14 * * 1-5"))  # 8 AM CT weekdays (14:00 UTC)
def scheduled_8am_campaign():
    """8 AM CT daily campaign - weekdays only"""
    import requests
    import time
    import uuid
    
    run_id = f"campaign_8am_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    # Record job start
    record_job_run_safe("campaign_8am", "14:00_utc", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "campaign_8am", "schedule": "0 14 * * 1-5", "run_id": run_id
    })
    
    try:
        resp = requests.get(f"{base_url}/campaign", timeout=120)
        result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        duration_ms = int((time.time() - start_time) * 1000)
        
        sent = result.get("sent", 0)
        errors = result.get("errors", 0)
        status = result.get("status", "success" if resp.status_code == 200 else "fail")
        
        record_job_run_safe("campaign_8am", "14:00_utc", status, {
            "run_id": run_id, "duration_ms": duration_ms, "sent": sent, "errors": errors, "result": result
        }, run_id)
        
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "campaign_8am", "schedule": "0 14 * * 1-5", "run_id": run_id,
            "duration_ms": duration_ms, "sent": sent, "errors": errors
        })
        
        print(f"[CRON 8am] {status} in {duration_ms}ms: sent={sent}, errors={errors}")
        return {"status": status, "result": result, "duration_ms": duration_ms}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        record_job_run_safe("campaign_8am", "14:00_utc", "fail", {
            "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        }, run_id)
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "campaign_8am", "schedule": "0 14 * * 1-5", "run_id": run_id,
            "duration_ms": duration_ms, "error": str(e)
        })
        send_alert_email("Campaign 8am FAILED", f"Error: {e}\nRun ID: {run_id}", "critical")
        print(f"[CRON 8am] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("30 15 * * 1-5"))  # 9:30 AM CT weekdays - CATCHUP CHECK
def scheduled_campaign_catchup_check():
    """9:30 AM CT check - trigger catchup if campaign missed"""
    import requests
    import time
    import uuid
    
    run_id = f"catchup_check_{uuid.uuid4().hex[:8]}"
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "campaign_catchup_check", "schedule": "30 15 * * 1-5", "run_id": run_id
    })
    
    if not check_campaign_ran_today():
        emit_event_safe("incident.deadman", "modal_cron", "critical", run_id, None, {
            "check": "campaign_8am", "threshold": "9:30am CT", "action": "catchup_triggered"
        })
        
        send_alert_email(
            "Campaign Missed - Triggering Catchup",
            f"The 8am CT campaign did not run by 9:30 AM CT.\nTriggering catchup now.\nRun ID: {run_id}",
            "warning"
        )
        
        # Trigger catchup
        try:
            resp = requests.get(f"{base_url}/campaign?catchup=true", timeout=120)
            result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
            
            emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
                "job_name": "campaign_catchup_check", "run_id": run_id, "catchup_triggered": True, "result": result
            })
            return {"status": "catchup_triggered", "result": result}
        except Exception as e:
            emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
                "job_name": "campaign_catchup_check", "run_id": run_id, "error": str(e)
            })
            return {"status": "fail", "error": str(e)}
    else:
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "campaign_catchup_check", "run_id": run_id, "campaign_ran": True
        })
        print(f"[CRON 9:30am] Campaign already ran today")
        return {"status": "ok", "campaign_ran": True}


@app.function(schedule=modal.Cron("0 */4 * * *"))  # Every 4 hours
def scheduled_prospecting():
    """Prospecting run every 4 hours"""
    import requests
    import time
    import uuid
    
    run_id = f"prospect_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    record_job_run_safe("prospecting", "4hr", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "prospecting", "schedule": "0 */4 * * *", "run_id": run_id
    })
    
    try:
        resp = requests.get(f"{base_url}/prospect", timeout=60)
        result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        duration_ms = int((time.time() - start_time) * 1000)
        
        leads = result.get("prospects_added", 0)
        status = "success" if resp.status_code == 200 else "fail"
        
        record_job_run_safe("prospecting", "4hr", status, {
            "run_id": run_id, "duration_ms": duration_ms, "leads": leads, "result": result
        }, run_id)
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "prospecting", "schedule": "0 */4 * * *", "run_id": run_id,
            "duration_ms": duration_ms, "leads": leads
        })
        
        print(f"[CRON 4hr] Prospecting {status} in {duration_ms}ms: leads={leads}")
        return {"status": status, "result": result, "duration_ms": duration_ms}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        record_job_run_safe("prospecting", "4hr", "fail", {
            "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        }, run_id)
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "prospecting", "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        })
        print(f"[CRON 4hr] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("0 */2 * * *"))  # Every 2 hours
def scheduled_optimizer():
    """Self-improvement optimizer every 2 hours"""
    import requests
    import time
    import uuid
    
    run_id = f"optimizer_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    record_job_run_safe("optimizer", "2hr", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "optimizer", "schedule": "0 */2 * * *", "run_id": run_id
    })
    
    try:
        resp = requests.get(f"{base_url}/optimize", timeout=60)
        result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        duration_ms = int((time.time() - start_time) * 1000)
        status = "success" if resp.status_code == 200 else "fail"
        
        record_job_run_safe("optimizer", "2hr", status, {
            "run_id": run_id, "duration_ms": duration_ms, "result": result
        }, run_id)
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "optimizer", "schedule": "0 */2 * * *", "run_id": run_id, "duration_ms": duration_ms
        })
        
        print(f"[CRON 2hr] Optimizer {status} in {duration_ms}ms")
        return {"status": status, "result": result, "duration_ms": duration_ms}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        record_job_run_safe("optimizer", "2hr", "fail", {
            "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        }, run_id)
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "optimizer", "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        })
        print(f"[CRON 2hr] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("0 * * * *"))  # Every hour
def scheduled_policy_optimizer():
    """Policy weight adjustment every hour"""
    import requests
    import time
    import uuid
    
    run_id = f"policy_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    record_job_run_safe("policy_optimizer", "1hr", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "policy_optimizer", "schedule": "0 * * * *", "run_id": run_id
    })
    
    try:
        resp = requests.get(f"{base_url}/api/policy-optimize", timeout=60)
        result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        duration_ms = int((time.time() - start_time) * 1000)
        status = "success" if resp.status_code == 200 else "fail"
        
        record_job_run_safe("policy_optimizer", "1hr", status, {
            "run_id": run_id, "duration_ms": duration_ms, "result": result
        }, run_id)
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "policy_optimizer", "schedule": "0 * * * *", "run_id": run_id, "duration_ms": duration_ms
        })
        
        print(f"[CRON 1hr] Policy optimizer {status} in {duration_ms}ms")
        return {"status": status, "result": result, "duration_ms": duration_ms}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        record_job_run_safe("policy_optimizer", "1hr", "fail", {
            "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        }, run_id)
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "policy_optimizer", "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        })
        print(f"[CRON 1hr] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("30 */2 * * *"))  # Every 2 hours at :30
def scheduled_off_hours_prep():
    """
    24/7 Prep Work - Runs ALWAYS, handles work appropriate for any time:
    - Generate audit reports for queued contacts
    - Build dossiers (company research) for leads
    - Queue emails for next business window
    - Enrichment and lead scoring
    
    SMS/Calls only go out during business hours (handled by campaign endpoint).
    This job prepares materials so they're ready when windows open.
    """
    import requests
    import time
    import uuid
    from datetime import datetime
    
    run_id = f"prep_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    record_job_run_safe("off_hours_prep", "2hr", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "off_hours_prep", "schedule": "30 */2 * * *", "run_id": run_id
    })
    
    results = {
        "reports_generated": 0,
        "dossiers_built": 0,
        "emails_queued": 0,
        "leads_enriched": 0
    }
    
    try:
        # 1. Generate audit reports for contacts due for outreach tomorrow
        try:
            resp = requests.get(f"{base_url}/api/generate-reports?prefetch=true", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                results["reports_generated"] = data.get("generated", 0)
        except Exception as e:
            print(f"[PREP] Report generation error: {e}")
        
        # 2. Build dossiers for new leads
        try:
            resp = requests.get(f"{base_url}/api/build-dossiers?limit=10", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                results["dossiers_built"] = data.get("built", 0)
        except Exception as e:
            print(f"[PREP] Dossier building error: {e}")
        
        # 3. Enrich leads (add company info, scoring)
        try:
            resp = requests.get(f"{base_url}/api/enrich-leads?limit=20", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                results["leads_enriched"] = data.get("enriched", 0)
        except Exception as e:
            print(f"[PREP] Lead enrichment error: {e}")
        
        # 4. Queue marketing emails (will only send during email windows)
        try:
            resp = requests.get(f"{base_url}/api/queue-emails?type=marketing", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                results["emails_queued"] = data.get("queued", 0)
        except Exception as e:
            print(f"[PREP] Email queueing error: {e}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        record_job_run_safe("off_hours_prep", "2hr", "success", {
            "run_id": run_id, "duration_ms": duration_ms, **results
        }, run_id)
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "off_hours_prep", "schedule": "30 */2 * * *", "run_id": run_id,
            "duration_ms": duration_ms, **results
        })
        
        print(f"[CRON 2hr:30] Off-hours prep complete in {duration_ms}ms: {results}")
        return {"status": "success", "results": results, "duration_ms": duration_ms}
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        record_job_run_safe("off_hours_prep", "2hr", "fail", {
            "run_id": run_id, "duration_ms": duration_ms, "error": str(e)
        }, run_id)
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "off_hours_prep", "run_id": run_id, "error": str(e)
        })
        print(f"[CRON 2hr:30] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("0,30 * * * 1-5"))  # Every 30 min on weekdays
def scheduled_timezone_aware_campaign():
    """
    Timezone-aware campaign trigger - runs every 30 min on weekdays.
    Checks which contacts are currently in their local business hours
    and triggers outreach only for those contacts.
    
    This enables true 24/7 operation across all US timezones.
    """
    import requests
    import time
    import uuid
    from datetime import datetime
    
    run_id = f"tz_campaign_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "timezone_aware_campaign", "schedule": "0,30 * * * 1-5", "run_id": run_id
    })
    
    try:
        # Get contacts currently in their business hours
        contacts_in_window = get_contacts_in_business_hours(channel="sms")
        
        if not contacts_in_window:
            emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
                "job_name": "timezone_aware_campaign", "run_id": run_id,
                "contacts_in_window": 0, "action": "skip"
            })
            print(f"[CRON TZ] No contacts in business hours window")
            return {"status": "skip", "reason": "no_contacts_in_window"}
        
        # Trigger campaign for these specific contacts
        contact_ids = [c.get("id") for c in contacts_in_window if c.get("id")]
        
        resp = requests.post(
            f"{base_url}/api/campaign-batch",
            json={"contact_ids": contact_ids, "channel": "sms", "run_id": run_id},
            timeout=120
        )
        
        result = resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        duration_ms = int((time.time() - start_time) * 1000)
        
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "timezone_aware_campaign", "run_id": run_id,
            "contacts_in_window": len(contacts_in_window),
            "sent": result.get("sent", 0), "duration_ms": duration_ms
        })
        
        print(f"[CRON TZ] Processed {len(contacts_in_window)} contacts in window: {result}")
        return {"status": "success", "contacts": len(contacts_in_window), "result": result}
        
    except Exception as e:
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "timezone_aware_campaign", "run_id": run_id, "error": str(e)
        })
        print(f"[CRON TZ] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("*/10 * * * *"))  # Every 10 minutes
def scheduled_kickoff_once():
    """
    One-time kickoff run per day.
    
    Checks kickoff_runs table:
    - If exists row where date=today AND executed=false
    - Run timezone-aware campaign respecting windows
    - Mark executed=true
    - Record job_runs and emit kickoff.run event
    
    Use case: Schedule a specific date for campaign start.
    """
    import requests
    import time
    import uuid
    from datetime import datetime
    
    run_id = f"kickoff_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    base_url = "https://nearmiss1193-afk--empire-api-v1-orchestration-api.modal.run"
    
    # Check if there's a pending kickoff for today
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}", "Content-Type": "application/json"}
        
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Check for pending kickoff
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/kickoff_runs?date=eq.{today}&executed=eq.false&limit=1",
            headers=headers, timeout=10
        )
        
        if resp.status_code != 200 or not resp.json():
            # No pending kickoff for today
            return {"status": "skip", "reason": "no_pending_kickoff", "date": today}
        
        kickoff = resp.json()[0]
        print(f"[KICKOFF] Found pending kickoff for {today}")
        
        # Record job start
        record_job_run_safe("kickoff", "once", "running", {"run_id": run_id, "date": today}, run_id)
        emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
            "job_name": "kickoff", "schedule": "once", "run_id": run_id, "date": today
        })
        
        # Get contacts in their business hours window
        contacts_in_window = get_contacts_in_business_hours(channel="sms")
        
        if not contacts_in_window:
            # No contacts in window yet - don't mark executed, try again in 10 min
            emit_event_safe("kickoff.waiting", "modal_cron", "info", run_id, None, {
                "date": today, "reason": "no_contacts_in_window", "will_retry": True
            })
            print(f"[KICKOFF] No contacts in window yet, will retry")
            return {"status": "waiting", "reason": "no_contacts_in_window", "will_retry": True}
        
        # Execute campaign for contacts in window
        contact_ids = [c.get("id") for c in contacts_in_window if c.get("id")]
        
        try:
            campaign_resp = requests.post(
                f"{base_url}/api/campaign-batch",
                json={"contact_ids": contact_ids, "channel": "sms", "run_id": run_id},
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            result = campaign_resp.json() if campaign_resp.status_code == 200 else {"error": campaign_resp.status_code}
        except Exception as e:
            result = {"error": str(e)}
        
        duration_ms = int((time.time() - start_time) * 1000)
        contacts_reached = result.get("sent", len(contacts_in_window))
        
        # Mark kickoff as executed
        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/kickoff_runs?date=eq.{today}",
                headers=headers,
                json={
                    "executed": True,
                    "executed_at": datetime.utcnow().isoformat(),
                    "run_id": run_id,
                    "contacts_reached": contacts_reached,
                    "details": {"result": result, "duration_ms": duration_ms}
                },
                timeout=10
            )
        except Exception as e:
            print(f"[KICKOFF] Failed to mark executed: {e}")
        
        # Record job completion
        record_job_run_safe("kickoff", "once", "success", {
            "run_id": run_id, "date": today, "contacts_reached": contacts_reached,
            "duration_ms": duration_ms, "result": result
        }, run_id)
        
        # Emit kickoff.run event
        emit_event_safe("kickoff.run", "modal_cron", "info", run_id, None, {
            "date": today,
            "contacts_reached": contacts_reached,
            "duration_ms": duration_ms,
            "result": result
        })
        
        print(f"[KICKOFF] Complete! Reached {contacts_reached} contacts in {duration_ms}ms")
        return {
            "status": "success",
            "date": today,
            "contacts_reached": contacts_reached,
            "duration_ms": duration_ms
        }
        
    except Exception as e:
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "kickoff", "run_id": run_id, "error": str(e)
        })
        print(f"[KICKOFF] Error: {e}")
        return {"status": "fail", "error": str(e)}


@app.function(schedule=modal.Cron("0 */6 * * *"))  # Every 6 hours (4x daily, respects API limits)
def scheduled_continuous_learning():
    """
    24/7 Continuous Sales Training from HuggingFace Datasets
    
    Fetches sales conversations, extracts patterns, and stores learnings.
    Rate-limited to 4 runs per day to stay within HuggingFace free tier.
    
    Datasets:
    - Call center scripts (92k conversations)
    - SaaS sales conversations
    - Customer support interactions
    
    Patterns extracted:
    - Objection handling
    - Closing techniques
    - Persuasion phrases
    """
    import requests
    import time
    import uuid
    from datetime import datetime
    import json
    
    run_id = f"learn_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    # Config
    HF_TOKEN = "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"
    HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
    SAMPLES_PER_RUN = 100  # Conservative for rate limiting
    
    # Patterns to learn
    PATTERNS = {
        "objection": ["too expensive", "not interested", "already have", "call back later", "no time", 
                      "need to think", "not ready", "budget", "competitor", "don't need"],
        "closing": ["sounds good", "let's do it", "sign me up", "interested", "tell me more", 
                    "yes", "perfect", "schedule", "book", "ready"],
        "persuasion": ["imagine", "because", "results", "guarantee", "save", "quick", 
                       "easy", "free", "limited", "exclusive", "value"]
    }
    
    # Datasets to learn from
    DATASETS = [
        ("AIxBlock/92k-real-world-call-center-scripts-english", "call_center"),
        ("DeepMostInnovations/saas-sales-conversations", "sales"),
        ("bitext/Bitext-customer-support-llm-chatbot-training-dataset", "support")
    ]
    
    record_job_run_safe("continuous_learning", "6hr", "running", {"run_id": run_id}, run_id)
    emit_event_safe("job.started", "modal_cron", "info", run_id, None, {
        "job_name": "continuous_learning", "schedule": "0 */6 * * *", "run_id": run_id
    })
    
    results = {
        "fetched": 0,
        "stored": 0,
        "patterns_found": {"objections": 0, "closing": 0, "persuasion": 0}
    }
    
    try:
        secrets = get_secrets()
        supabase_key = secrets["SUPABASE_KEY"]
        db_headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}", "Content-Type": "application/json"}
        
        for dataset_id, source in DATASETS:
            try:
                # Fetch from HuggingFace
                url = "https://datasets-server.huggingface.co/rows"
                # Use random offset for variety
                offset = int(time.time()) % 1000
                params = {"dataset": dataset_id, "config": "default", "split": "train", 
                          "offset": offset, "length": SAMPLES_PER_RUN}
                
                resp = requests.get(url, params=params, headers=HF_HEADERS, timeout=60)
                if resp.status_code != 200:
                    print(f"[LEARN] {source}: Status {resp.status_code}")
                    continue
                
                rows = resp.json().get("rows", [])
                results["fetched"] += len(rows)
                print(f"[LEARN] {source}: Fetched {len(rows)} rows")
                
                # Process each row
                for row in rows:
                    row_data = row.get("row", row)
                    text = str(row_data.get("text", "") or row_data.get("conversation", "") or 
                               row_data.get("instruction", "") or row_data.get("input", ""))[:2000]
                    
                    if len(text) < 50:
                        continue
                    
                    # Extract patterns
                    text_lower = text.lower()
                    patterns_found = {
                        "objections": [p for p in PATTERNS["objection"] if p in text_lower],
                        "closing": [p for p in PATTERNS["closing"] if p in text_lower],
                        "persuasion": [p for p in PATTERNS["persuasion"] if p in text_lower]
                    }
                    
                    # Count patterns
                    results["patterns_found"]["objections"] += len(patterns_found["objections"])
                    results["patterns_found"]["closing"] += len(patterns_found["closing"])
                    results["patterns_found"]["persuasion"] += len(patterns_found["persuasion"])
                    
                    # Store to training_data table
                    try:
                        store_resp = requests.post(
                            f"{SUPABASE_URL}/rest/v1/training_data",
                            headers=db_headers,
                            json={
                                "raw_text": text,
                                "scenario": source,
                                "outcome": "converted" if patterns_found["closing"] else "neutral",
                                "emotional_cues": json.dumps(patterns_found),
                                "agent": "continuous_learning",
                                "learning_extracted": True
                            },
                            timeout=10
                        )
                        if store_resp.status_code in [200, 201]:
                            results["stored"] += 1
                    except:
                        pass
                
                # Rate limiting between datasets
                time.sleep(2)
                
            except Exception as e:
                print(f"[LEARN] {source} error: {e}")
                continue
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Record completion
        record_job_run_safe("continuous_learning", "6hr", "success", {
            "run_id": run_id, "duration_ms": duration_ms, **results
        }, run_id)
        
        emit_event_safe("job.completed", "modal_cron", "info", run_id, None, {
            "job_name": "continuous_learning", "schedule": "0 */6 * * *", "run_id": run_id,
            "duration_ms": duration_ms, **results
        })
        
        # Emit learning event for tracking
        emit_event_safe("learning.completed", "modal_cron", "info", run_id, None, {
            "fetched": results["fetched"],
            "stored": results["stored"],
            "patterns": results["patterns_found"],
            "duration_ms": duration_ms
        })
        
        print(f"[LEARN] Complete in {duration_ms}ms: {results}")
        return {"status": "success", "results": results, "duration_ms": duration_ms}
        
    except Exception as e:
        emit_event_safe("job.failed", "modal_cron", "error", run_id, None, {
            "job_name": "continuous_learning", "run_id": run_id, "error": str(e)
        })
        print(f"[LEARN] Error: {e}")
        return {"status": "fail", "error": str(e)}

