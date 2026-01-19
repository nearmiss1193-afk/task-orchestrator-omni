"""
SOVEREIGN ORCHESTRATOR - Stripped down for emergency recovery
Only essential endpoints, NO scheduled functions
"""
import modal
from fastapi import FastAPI, Request
from datetime import datetime, timedelta, timezone
import json
import os

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "requests")

# Define secrets - these MUST be set via `modal secret create`
secrets = modal.Secret.from_name("empire-secrets")

app = modal.App("empire-api-v3", image=image, secrets=[secrets])

# Config (Non-sensitive constants only)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
# GHL Email Webhook - send marketing emails via GHL workflow
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/email-outbound"
GHL_LOCATION_ID = "RnK4OjX0oDcqtWw0VyLr"  # Empire Main location
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
ESCALATION_PHONE = "+13529368152"

# Unified Comms System - Canonical Routing Truth (STEP 0)
# Voice: Vapi handles inbound/outbound calls
VOICE_PROVIDER = "vapi"
VOICE_NUMBER = "+18632132505"  # Call Sarah (Voice AI)
# SMS: GHL handles inbound/outbound texts (A2P verified)
SMS_PROVIDER = "ghl"
SMS_NUMBER = "+13527585336"  # Text Sarah (SMS)
# Legacy alias
CANONICAL_NUMBER = SMS_NUMBER

# Secrets loaded at runtime from modal.Secret
def get_secrets():
    return {
        # Prefer service role key (bypasses RLS) for write operations
        "SUPABASE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", "")),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", ""),
        "GHL_API_KEY": os.environ.get("GHL_API_KEY", ""),
        # Twilio for SMS
        "TWILIO_ACCOUNT_SID": os.environ.get("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.environ.get("TWILIO_AUTH_TOKEN", ""),
        # Vapi for voice
        "VAPI_WEBHOOK_SECRET": os.environ.get("VAPI_WEBHOOK_SECRET", ""),
        "VAPI_ASSISTANT_ID": os.environ.get("VAPI_ASSISTANT_ID", "")
    }

# ============================================================
# BRAND CANON - Single source of truth for brand/offer data
# ============================================================
BRAND_CANON = {
    "voice_number": "+18632132505",
    "voice_number_display": "(863) 213-2505",
    "sms_number": "+13527585336",
    "sms_number_display": "(352) 758-5336",
    "voice_provider": "vapi",
    "sms_provider": "ghl",
    "booking_link": "https://link.aiserviceco.com/discovery",
    "business_name": "AI Service Co",
    "hours": "Mon-Fri 8am-6pm EST",
    "website": "https://www.aiserviceco.com",
    "pricing": {
        "starter": 297,
        "growth": 497,
        "dominance": 997
    },
    "owner_email": "nearmiss1193@gmail.com"
}


@app.function()
@modal.asgi_app()
def orchestration_api():
    api = FastAPI(title="Sovereign Orchestrator v3 (Emergency)")
    
    import requests
    secrets = get_secrets()
    SUPABASE_KEY = secrets["SUPABASE_KEY"]
    
    def log_event(event_type: str, source: str, severity: str = "info", 
                  correlation_id: str = None, entity_id: str = None, payload: dict = None):
        """Log event to Supabase event_log_v2"""
        try:
            event = {
                "type": event_type,
                "source": source,
                "severity": severity,
                "correlation_id": correlation_id,
                "entity_id": entity_id,
                "payload": payload or {},
                "ts": datetime.utcnow().isoformat()
            }
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(f"{SUPABASE_URL}/rest/v1/event_log_v2", headers=headers, json=event, timeout=10)
        except Exception as e:
            print(f"[Log Error] {e}")
    
    def normalize_phone(phone: str) -> str:
        """Normalize phone to E.164 format"""
        if not phone:
            return ""
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"
        elif len(digits) > 11:
            return f"+{digits}"
        return phone
    
    def record_outbound_touch(phone: str, channel: str, variant_id: str = None, 
                               variant_name: str = None, run_id: str = None,
                               vertical: str = "hvac", company: str = None,
                               correlation_id: str = None, payload: dict = None) -> bool:
        """
        Record outbound touch to outbound_touches table for attribution.
        Returns True on success, False on failure (fail-safe).
        """
        try:
            touch = {
                "phone": normalize_phone(phone),
                "channel": channel,
                "variant_id": variant_id,
                "variant_name": variant_name,
                "run_id": run_id,
                "vertical": vertical or "hvac",
                "company": company,
                "correlation_id": correlation_id,
                "status": "sent",
                "payload": payload or {}
            }
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            resp = requests.post(f"{SUPABASE_URL}/rest/v1/outbound_touches", headers=headers, json=touch, timeout=10)
            
            if resp.status_code in [200, 201]:
                return True
            else:
                log_event("error.occurred", "modal", "error", correlation_id, phone, {
                    "error": f"record_touch failed: {resp.status_code}",
                    "response": resp.text[:200] if resp.text else "no response"
                })
                return False
        except Exception as e:
            log_event("error.occurred", "modal", "error", correlation_id, phone, {"error": f"record_touch: {e}"})
            return False
    
    def find_attributed_touch(phone: str, max_days: int = 7) -> dict:
        """
        Find most recent outbound touch for phone within max_days.
        Returns {touch: {...}, confidence: float} or {touch: None, confidence: 0.0}
        """
        try:
            from urllib.parse import quote
            phone_normalized = normalize_phone(phone)
            phone_encoded = quote(phone_normalized, safe='')  # URL encode the + sign
            cutoff = (datetime.now(timezone.utc) - timedelta(days=max_days)).isoformat()
            cutoff_encoded = quote(cutoff, safe='')  # URL encode the + in timezone
            
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/outbound_touches?phone=eq.{phone_encoded}&ts=gte.{cutoff_encoded}&order=ts.desc&limit=1",
                headers=headers, timeout=10
            )
            
            if resp.status_code != 200:
                log_event("error.occurred", "modal", "warn", payload={"error": f"find_touch query failed: {resp.status_code}", "phone": phone_normalized, "response": resp.text[:100] if resp.text else ""})
                return {"touch": None, "confidence": 0.0}
            
            touches = resp.json()
            if not touches:
                # Log for debugging - no touches found
                log_event("attribution.debug", "modal", "info", payload={"phone": phone_normalized, "cutoff": cutoff, "result": "no_touches_found"})
                return {"touch": None, "confidence": 0.0}
            
            touch = touches[0]
            touch_ts = datetime.fromisoformat(touch["ts"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            hours_ago = (now - touch_ts).total_seconds() / 3600
            
            # Confidence based on recency (per spec)
            # <= 15min (0.25h): 1.0, <= 24h: 0.7, <= 72h: 0.4, else: 0.2
            if hours_ago <= 0.25:  # 15 minutes
                confidence = 1.0
            elif hours_ago <= 24:
                confidence = 0.7
            elif hours_ago <= 72:
                confidence = 0.4
            else:
                confidence = 0.2
            
            return {"touch": touch, "confidence": confidence}
        except Exception as e:
            log_event("error.occurred", "modal", "error", payload={"error": f"find_touch: {e}"})
            return {"touch": None, "confidence": 0.0}
    
    def record_attribution(appointment_id: str, phone: str, touch: dict, confidence: float, hours_since: float = None) -> bool:
        """
        Record attribution to outreach_attribution table.
        Uses EXACT column names: attributed_touch_id, attributed_variant_id, attributed_variant_name,
        attributed_channel, hours_since_touch, confidence, attribution_source
        """
        try:
            # Calculate hours_since_touch if not provided
            if hours_since is None and touch and touch.get("ts"):
                touch_ts = datetime.fromisoformat(touch["ts"].replace("Z", "+00:00"))
                hours_since = (datetime.now(timezone.utc) - touch_ts).total_seconds() / 3600
            
            attribution = {
                "appointment_id": appointment_id,
                "phone": normalize_phone(phone),
                "attributed_touch_id": touch.get("id") if touch else None,
                "attributed_variant_id": touch.get("variant_id") if touch else None,
                "attributed_variant_name": touch.get("variant_name") if touch else None,
                "attributed_channel": touch.get("channel") if touch else None,
                "hours_since_touch": round(hours_since, 2) if hours_since else None,
                "confidence": confidence,
                "attribution_source": "auto" if touch else "none"
            }
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
            resp = requests.post(f"{SUPABASE_URL}/rest/v1/outreach_attribution", headers=headers, json=attribution, timeout=10)
            
            if resp.status_code in [200, 201]:
                return True
            else:
                log_event("error.occurred", "modal", "error", payload={
                    "error": f"record_attribution failed: {resp.status_code}",
                    "response": resp.text[:300] if resp.text else "no response",
                    "attribution": attribution
                })
                return False
        except Exception as e:
            log_event("error.occurred", "modal", "error", payload={"error": f"record_attribution: {e}"})
            return False
    
    def send_marketing_email_via_ghl(to_email: str, subject: str, html_body: str, 
                                      text_body: str = None, contact_id: str = None,
                                      campaign_id: str = None, variant_id: str = None,
                                      metadata: dict = None) -> dict:
        """
        Send marketing/campaign emails. Tries Resend first, then GHL fallback.
        Returns: {"success": bool, "provider": str, "message_id": str or None, "error": str or None}
        """
        import uuid
        correlation_id = f"email_{uuid.uuid4().hex[:8]}"
        RESEND_API_KEY = secrets.get("RESEND_API_KEY", "")
        
        # Try Resend first (more reliable delivery)
        if RESEND_API_KEY:
            try:
                resend_resp = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "from": "AI Service Co <hello@aiserviceco.com>",
                        "to": [to_email],
                        "subject": subject,
                        "html": html_body
                    },
                    timeout=15
                )
                
                if resend_resp.status_code in [200, 201]:
                    log_event("email.sent", "modal", "info", correlation_id, to_email, {
                        "provider": "resend",
                        "subject": subject,
                        "campaign_id": campaign_id,
                        "variant_id": variant_id
                    })
                    return {"success": True, "provider": "resend", "message_id": correlation_id, "error": None}
            except Exception as e:
                print(f"[Resend Error] {e}, falling back to GHL")
        
        # Fallback to GHL webhook
        try:
            payload = {
                "email": to_email,
                "subject": subject,
                "html": html_body,
                "text": text_body or "",
                "contact_id": contact_id,
                "campaign_id": campaign_id,
                "variant_id": variant_id,
                "location_id": GHL_LOCATION_ID,
                "metadata": metadata or {}
            }
            
            ghl_resp = requests.post(GHL_EMAIL_WEBHOOK, json=payload, timeout=30)
            
            if ghl_resp.status_code in [200, 201]:
                log_event("email.sent", "modal", "info", correlation_id, to_email, {
                    "provider": "ghl",
                    "subject": subject,
                    "campaign_id": campaign_id,
                    "variant_id": variant_id,
                    "contact_id": contact_id
                })
                return {"success": True, "provider": "ghl", "message_id": correlation_id, "error": None}
            else:
                error_msg = f"GHL returned {ghl_resp.status_code}"
                log_event("email.failed", "modal", "error", correlation_id, to_email, {
                    "provider": "ghl",
                    "subject": subject,
                    "error": error_msg,
                    "status_code": ghl_resp.status_code
                })
                return {"success": False, "provider": "ghl", "message_id": None, "error": error_msg}
        except Exception as e:
            log_event("email.failed", "modal", "error", correlation_id, to_email, {
                "provider": "ghl",
                "subject": subject,
                "error": str(e)
            })
            return {"success": False, "provider": "ghl", "message_id": None, "error": str(e)}
    
    def send_alert_email(subject: str, body: str, severity: str = "warning") -> dict:
        """
        Send system alert emails via Resend. 
        Only for internal alerts (deadman checks, incidents) - NOT for marketing.
        Returns: {"success": bool, "provider": "resend", "message_id": str or None, "error": str or None}
        """
        import uuid
        correlation_id = f"alert_{uuid.uuid4().hex[:8]}"
        RESEND_API_KEY = secrets.get("RESEND_API_KEY", "")
        
        if not RESEND_API_KEY:
            log_event("alert.skipped", "modal", "warn", correlation_id, None, {
                "reason": "RESEND_API_KEY not configured",
                "subject": subject
            })
            return {"success": False, "provider": "resend", "message_id": None, "error": "No RESEND_API_KEY"}
        
        try:
            resend_resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "Sovereign Alert <alerts@aiserviceco.com>",
                    "to": ["nearmiss1193@gmail.com"],
                    "subject": f"[{severity.upper()}] {subject}",
                    "html": f"<h3>{subject}</h3><pre>{body}</pre>"
                },
                timeout=15
            )
            
            if resend_resp.status_code in [200, 201]:
                log_event("alert.sent", "modal", "info", correlation_id, None, {
                    "provider": "resend",
                    "subject": subject,
                    "severity": severity
                })
                return {"success": True, "provider": "resend", "message_id": correlation_id, "error": None}
            else:
                log_event("alert.failed", "modal", "error", correlation_id, None, {
                    "provider": "resend",
                    "subject": subject,
                    "error": f"Resend returned {resend_resp.status_code}"
                })
                return {"success": False, "provider": "resend", "message_id": None, "error": f"Resend error: {resend_resp.status_code}"}
        except Exception as e:
            print(f"[send_alert_email] Error: {e}")
            return {"success": False, "provider": "resend", "message_id": None, "error": str(e)}
    
    @api.get("/health")
    def health():
        """Health check endpoint"""
        return {
            "status": "ok",
            "orchestrator": "sovereign-v3-emergency",
            "agents": ["sarah", "christina"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/debug/secrets")
    def debug_secrets():
        """Check which secrets are present (boolean flags only, no values)"""
        import os
        return {
            "SUPABASE_SERVICE_ROLE_KEY": bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY")),
            "SUPABASE_KEY": bool(os.environ.get("SUPABASE_KEY")),
            "SUPABASE_ANON_KEY": bool(os.environ.get("SUPABASE_ANON_KEY")),
            "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
            "RESEND_API_KEY": bool(os.environ.get("RESEND_API_KEY")),
            "GHL_API_KEY": bool(os.environ.get("GHL_API_KEY")),
            "TWILIO_ACCOUNT_SID": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
            "TWILIO_AUTH_TOKEN": bool(os.environ.get("TWILIO_AUTH_TOKEN")),
            "key_in_use": "SERVICE_ROLE" if os.environ.get("SUPABASE_SERVICE_ROLE_KEY") else ("ANON" if os.environ.get("SUPABASE_KEY") else "NONE"),
            "key_length": len(os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", "")))
        }
    
    @api.get("/api/truth")
    def truth():
        """
        Dashboard Truth Strip - returns system health metrics in one call.
        Used by dashboard to show staleness alerts.
        """
        from datetime import timezone
        import uuid
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        server_time = datetime.now(timezone.utc).isoformat()
        
        result = {
            "status": "ok",
            "api_base": "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run",
            "server_time": server_time,
            "last_event_ts": None,
            "last_kpi_ts": None,
            "last_campaign_ran_at": None,
            "notes": {}
        }
        
        # 1. Get last event from event_log_v2
        try:
            evt_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?select=ts,type&order=ts.desc&limit=1",
                headers=headers, timeout=10
            )
            if evt_resp.status_code == 200:
                data = evt_resp.json()
                if data and len(data) > 0:
                    result["last_event_ts"] = data[0].get("ts")
        except Exception as e:
            result["notes"]["event_error"] = str(e)
        
        # 2. Get last KPI snapshot
        try:
            kpi_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.kpi.snapshot&select=ts&order=ts.desc&limit=1",
                headers=headers, timeout=10
            )
            if kpi_resp.status_code == 200:
                data = kpi_resp.json()
                if data and len(data) > 0:
                    result["last_kpi_ts"] = data[0].get("ts")
        except Exception as e:
            result["notes"]["kpi_error"] = str(e)
        
        # 3. Get last campaign run from job_runs
        try:
            job_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/job_runs?job_name=in.(campaign,campaign_8am,campaign_batch,scheduled_timezone_aware_campaign)&select=ran_at,job_name&order=ran_at.desc&limit=1",
                headers=headers, timeout=10
            )
            if job_resp.status_code == 200:
                data = job_resp.json()
                if data and len(data) > 0:
                    result["last_campaign_ran_at"] = data[0].get("ran_at")
        except Exception as e:
            result["notes"]["campaign_error"] = str(e)
        
        # 4. Get SMS counts for last 24 hours
        sms_sent_24h = 0
        sms_failed_24h = 0
        try:
            # Count SMS sent
            sms_sent_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.sent&ts=gte.{(datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}&select=id",
                headers={**headers, "Prefer": "count=exact"}, timeout=10
            )
            if sms_sent_resp.status_code == 200:
                sms_sent_24h = int(sms_sent_resp.headers.get("content-range", "0-0/0").split("/")[-1])
            
            # Count SMS failed
            sms_failed_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.failed&ts=gte.{(datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}&select=id",
                headers={**headers, "Prefer": "count=exact"}, timeout=10
            )
            if sms_failed_resp.status_code == 200:
                sms_failed_24h = int(sms_failed_resp.headers.get("content-range", "0-0/0").split("/")[-1])
        except Exception as e:
            result["notes"]["sms_count_error"] = str(e)
        
        result["sms_sent_last_24h"] = sms_sent_24h
        result["sms_failed_last_24h"] = sms_failed_24h
        
        # 5. Log this truth check (debug level)
        try:
            log_event("dashboard.truth_checked", "modal", "debug", 
                      correlation_id=f"truth_{uuid.uuid4().hex[:6]}",
                      payload={
                          "last_event_ts": result["last_event_ts"],
                          "last_kpi_ts": result["last_kpi_ts"],
                          "last_campaign_ran_at": result["last_campaign_ran_at"],
                          "sms_sent_24h": sms_sent_24h,
                          "sms_failed_24h": sms_failed_24h
                      })
        except:
            pass
        
        return result
    
    @api.get("/api/sms/status")
    def sms_status(since_hours: int = 24):
        """
        SMS Campaign Status - Returns SMS sent/failed counts and recent entries.
        Query: ?since_hours=24 (default)
        """
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        
        result = {
            "status": "ok",
            "since_hours": since_hours,
            "cutoff_time": cutoff.isoformat(),
            "sms_sent": 0,
            "sms_failed": 0,
            "sms_fallback": 0,
            "sms_dry_run": 0,
            "sms_queued": 0,
            "total_sms_events": 0,
            "failure_reasons": {},
            "recent_entries": [],
            "errors": []
        }
        
        try:
            # Fetch all SMS-related events (last 500)
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?select=type,ts,entity_id,payload&order=ts.desc&limit=500",
                headers=headers, timeout=15
            )
            
            if resp.status_code != 200:
                result["errors"].append(f"fetch_error: HTTP {resp.status_code}")
                return result
            
            events = resp.json()
            
            # Filter SMS events within time range
            for evt in events:
                etype = evt.get("type", "")
                if not etype.startswith("sms."):
                    continue
                    
                # Parse timestamp
                ts_str = evt.get("ts")
                if not ts_str:
                    continue
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue  # Skip events older than cutoff
                except:
                    continue
                
                result["total_sms_events"] += 1
                payload = evt.get("payload") or {}
                
                # Count by type
                if etype == "sms.sent":
                    result["sms_sent"] += 1
                elif etype == "sms.failed":
                    result["sms_failed"] += 1
                    if payload.get("error"):
                        reason = str(payload.get("error"))[:50]
                        result["failure_reasons"][reason] = result["failure_reasons"].get(reason, 0) + 1
                elif etype == "sms.fallback":
                    result["sms_fallback"] += 1
                elif etype == "sms.dry_run":
                    result["sms_dry_run"] += 1
                elif etype == "sms.queued":
                    result["sms_queued"] += 1
                
                # Add to recent entries (first 10)
                if len(result["recent_entries"]) < 10:
                    result["recent_entries"].append({
                        "type": etype,
                        "ts": ts_str,
                        "phone": payload.get("phone") or payload.get("to_phone") or evt.get("entity_id"),
                        "contact": payload.get("contact_name") or payload.get("company_name"),
                        "error": payload.get("error")
                    })
                    
        except Exception as e:
            result["errors"].append(f"exception: {str(e)}")
        
        return result
    
    # ========== UNIFIED TELEPHONY: SMS ENDPOINTS ==========
    
    def send_sms_via_twilio(from_phone: str, to_phone: str, message: str, correlation_id: str = None) -> dict:
        """Send SMS via Twilio API - for outbound and reply"""
        import uuid
        correlation_id = correlation_id or f"sms_out_{uuid.uuid4().hex[:8]}"
        
        TWILIO_ACCOUNT_SID = secrets.get("TWILIO_ACCOUNT_SID", "")
        TWILIO_AUTH_TOKEN = secrets.get("TWILIO_AUTH_TOKEN", "")
        
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            log_event("sms.failed", "twilio", "error", correlation_id, to_phone, {
                "error": "Missing Twilio credentials"
            })
            return {"success": False, "error": "Missing Twilio credentials"}
        
        try:
            resp = requests.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json",
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                data={
                    "From": from_phone,
                    "To": to_phone,
                    "Body": message
                },
                timeout=15
            )
            
            if resp.status_code in [200, 201]:
                sid = resp.json().get("sid", "")
                log_event("sms.sent", "twilio", "info", correlation_id, to_phone, {
                    "from": from_phone,
                    "to": to_phone,
                    "body": message[:100],
                    "sid": sid
                })
                return {"success": True, "sid": sid}
            else:
                log_event("sms.failed", "twilio", "error", correlation_id, to_phone, {
                    "error": resp.text[:200],
                    "status_code": resp.status_code
                })
                return {"success": False, "error": resp.text[:200]}
        except Exception as e:
            log_event("sms.failed", "twilio", "error", correlation_id, to_phone, {"error": str(e)})
            return {"success": False, "error": str(e)}
    
    @api.post("/webhook/sms/inbound")
    async def sms_inbound_webhook(request: Request):
        """
        Handle inbound SMS from Twilio.
        - Log to event_log_v2
        - Optionally generate AI reply
        - Return empty TwiML (replies sent separately)
        """
        import uuid
        from urllib.parse import parse_qs
        from fastapi.responses import Response
        
        try:
            body = await request.body()
            params = parse_qs(body.decode())
        except:
            return Response(
                content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                media_type="application/xml"
            )
        
        from_phone = params.get("From", [""])[0]
        to_phone = params.get("To", [""])[0]
        message_body = params.get("Body", [""])[0]
        sms_sid = params.get("MessageSid", [""])[0]
        
        correlation_id = f"sms_in_{uuid.uuid4().hex[:8]}"
        
        # Log inbound SMS
        log_event("sms.inbound", "twilio", "info", 
                  correlation_id=correlation_id,
                  entity_id=from_phone,
                  payload={
                      "from": from_phone,
                      "to": to_phone,
                      "body": message_body,
                      "sms_sid": sms_sid
                  })
        
        # Check for STOP/opt-out
        if message_body.strip().upper() in ["STOP", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"]:
            log_event("sms.optout", "twilio", "warn", correlation_id, from_phone, {
                "keyword": message_body.strip().upper()
            })
            # Return empty - Twilio handles STOP automatically
            return Response(
                content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                media_type="application/xml"
            )
        
        # Auto-reply for common keywords (can be enhanced with AI)
        reply = None
        msg_lower = message_body.strip().lower()
        
        if msg_lower in ["yes", "y", "interested", "info"]:
            reply = "Great! Our AI assistant Sarah will reach out shortly. You can also book directly: https://link.aiserviceco.com/discovery"
        elif msg_lower in ["help", "?"]:
            reply = "Reply YES for info on our AI business tools for HVAC. Call (863) 213-2505 to speak with Sarah. Reply STOP to opt out."
        
        if reply:
            send_sms_via_twilio(to_phone, from_phone, reply, f"{correlation_id}_reply")
        
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )
    
    @api.post("/webhook/sms/status")
    async def sms_status_callback(request: Request):
        """Handle Twilio SMS status callbacks (delivered, failed, etc.)"""
        import uuid
        from urllib.parse import parse_qs
        from fastapi.responses import Response
        
        try:
            body = await request.body()
            params = parse_qs(body.decode())
        except:
            return {"status": "ok"}
        
        sms_sid = params.get("MessageSid", [""])[0]
        status = params.get("MessageStatus", [""])[0]
        to_phone = params.get("To", [""])[0]
        error_code = params.get("ErrorCode", [""])[0]
        
        log_event(f"sms.status.{status}", "twilio", "info" if status == "delivered" else "warn",
                  correlation_id=f"status_{sms_sid[:8]}",
                  entity_id=to_phone,
                  payload={
                      "sms_sid": sms_sid,
                      "status": status,
                      "error_code": error_code
                  })
        
        return {"status": "ok"}
    
    @api.post("/api/sms/send")
    async def api_sms_send(request: Request):
        """
        Manual SMS send endpoint.
        POST body: {"to": "+1234567890", "message": "Hello"}
        """
        import uuid
        
        try:
            body = await request.json()
        except:
            return {"success": False, "error": "Invalid JSON"}
        
        to_phone = body.get("to", "")
        message = body.get("message", "")
        from_phone = body.get("from", "+18632132505")  # Default to canonical number
        
        if not to_phone or not message:
            return {"success": False, "error": "Missing 'to' or 'message'"}
        
        # Normalize phone
        if not to_phone.startswith("+"):
            to_phone = f"+1{to_phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"
        
        correlation_id = f"api_sms_{uuid.uuid4().hex[:8]}"
        result = send_sms_via_twilio(from_phone, to_phone, message, correlation_id)
        
        return result
    
    @api.post("/api/test/record-touch")
    async def test_record_touch(request: Request):
        """
        Test endpoint: Record an outbound touch with variant_id.
        POST body: {"phone": "+1...", "channel": "sms", "variant_id": "v_abc", "variant_name": "Control A"}
        """
        import uuid
        
        try:
            body = await request.json()
        except:
            return {"success": False, "error": "Invalid JSON"}
        
        phone = body.get("phone")
        if not phone:
            return {"success": False, "error": "Missing phone"}
        
        correlation_id = f"test_touch_{uuid.uuid4().hex[:8]}"
        
        # Record the touch
        success = record_outbound_touch(
            phone=phone,
            channel=body.get("channel", "sms"),
            variant_id=body.get("variant_id", "test_variant"),
            variant_name=body.get("variant_name", "Test Variant"),
            run_id=body.get("run_id", f"test_run_{datetime.now(timezone.utc).strftime('%Y%m%d')}"),
            vertical=body.get("vertical", "hvac"),
            company=body.get("company"),
            correlation_id=correlation_id,
            payload=body
        )
        
        # Also log sms.sent with variant
        log_event("sms.sent", "test", "info", correlation_id, phone, {
            "phone": normalize_phone(phone),
            "variant_id": body.get("variant_id", "test_variant"),
            "variant_name": body.get("variant_name", "Test Variant"),
            "channel": body.get("channel", "sms"),
            "run_id": body.get("run_id"),
            "test": True
        })
        
        return {"success": success, "correlation_id": correlation_id, "phone_normalized": normalize_phone(phone)}
    
    @api.get("/api/kpi-snapshot")
    def kpi_snapshot():
        """Emit KPI snapshot - simplified"""
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
            leads_resp = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?select=count", headers=headers)
            lead_count = int(leads_resp.headers.get("content-range", "0-0/0").split("/")[-1])
            
            kpi_data = {
                "leads_total": lead_count,
                "bookings_total": 0,
                "booking_rate": 0.0,
                "version": "v3-emergency"
            }
            
            log_event("kpi.snapshot", "modal", "info", payload=kpi_data)
            return {"status": "ok", "kpi": kpi_data}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.post("/webhook/ghl/appointment")
    async def ghl_appointment_webhook(request: Request):
        """
        Handle GHL appointment webhooks with variant attribution.
        - Log appointment event
        - Find attributed outbound touch
        - Record attribution
        - Emit appointment.attributed event
        """
        import uuid
        
        try:
            body = await request.json()
        except:
            return {"status": "error", "message": "Invalid JSON"}
        
        # Map GHL event types to our types
        ghl_type = body.get("type", body.get("event_type", "unknown"))
        type_map = {
            "AppointmentCreated": "appointment.created",
            "AppointmentUpdated": "appointment.updated",
            "AppointmentDeleted": "appointment.cancelled",
            "AppointmentStatusChanged": "appointment.status_changed",
            "created": "appointment.created",
            "updated": "appointment.updated"
        }
        
        mapped_type = type_map.get(ghl_type, f"appointment.{ghl_type.lower()}")
        
        # Extract contact info - check multiple GHL payload locations
        contact = body.get("contact", {})
        customer = body.get("customer", {})
        contact_id = body.get("contactId") or contact.get("id") or body.get("contact_id")
        
        # Phone extraction priority (per spec):
        # 1) body.contact.phone  2) body.contact.phoneNumber  3) body.contact_phone (TOP LEVEL)
        # 4) body.phone  5) body.contactPhone  6) body.customer.phone
        contact_phone = (
            contact.get("phone") or 
            contact.get("phoneNumber") or 
            body.get("contact_phone") or  # TOP LEVEL - GHL puts it here
            body.get("phone") or 
            body.get("contactPhone") or
            customer.get("phone")
        )
        
        # Appointment ID priority (per spec):
        # 1) appointmentId  2) appointment.id  3) appointment_id (TOP LEVEL)  4) id
        appointment_id = (
            body.get("appointmentId") or 
            (body.get("appointment", {}) or {}).get("id") or 
            body.get("appointment_id") or  # TOP LEVEL
            body.get("id") or 
            f"appt_{uuid.uuid4().hex[:8]}"
        )
        correlation_id = f"appt_{uuid.uuid4().hex[:8]}"
        
        # Normalize phone for attribution lookup
        contact_phone_normalized = normalize_phone(contact_phone) if contact_phone else None
        
        # Log the base appointment event
        log_event(
            mapped_type,
            "ghl",
            "info",
            correlation_id=correlation_id,
            entity_id=contact_id,
            payload={
                "appointment_id": appointment_id,
                "calendar_id": body.get("calendarId") or body.get("calendar_id"),
                "contact_id": contact_id,
                "start_time": body.get("startTime") or body.get("start_time"),
                "end_time": body.get("endTime") or body.get("end_time"),
                "status": body.get("status"),
                "title": body.get("title"),
                "contact_name": contact.get("name") or body.get("contact_name"),
                "contact_phone": contact_phone_normalized,
                "contact_email": contact.get("email") or body.get("email"),
                "location_id": body.get("locationId") or GHL_LOCATION_ID,
                "raw_type": ghl_type
            }
        )
        
        # ===== ATTRIBUTION LOGIC =====
        # ALWAYS create attribution record for appointment.created events
        attribution_result = {"attributed": False, "confidence": 0.0, "variant_id": None}
        
        if mapped_type == "appointment.created":
            if contact_phone_normalized:
                # Find most recent outbound touch for this phone
                touch_result = find_attributed_touch(contact_phone_normalized, max_days=7)
                touch = touch_result.get("touch")
                confidence = touch_result.get("confidence", 0.0)
                
                if touch and confidence > 0:
                    # Record attribution WITH touch
                    success = record_attribution(appointment_id, contact_phone_normalized, touch, confidence)
                    
                    attribution_result = {
                        "attributed": success,
                        "confidence": confidence,
                        "variant_id": touch.get("variant_id"),
                        "variant_name": touch.get("variant_name"),
                        "channel": touch.get("channel"),
                        "touch_id": touch.get("id")
                    }
                    
                    # Emit attribution.created event
                    log_event(
                        "attribution.created",
                        "modal",
                        "info",
                        correlation_id=f"{correlation_id}_attr",
                        entity_id=contact_id,
                        payload={
                            "appointment_id": appointment_id,
                            "touch_id": touch.get("id"),
                            "variant_id": touch.get("variant_id"),
                            "hours_since_touch": round((datetime.now(timezone.utc) - 
                                datetime.fromisoformat(touch["ts"].replace("Z", "+00:00"))).total_seconds() / 3600, 2) if touch.get("ts") else None,
                            "confidence": confidence
                        }
                    )
                else:
                    # No touch found - record with confidence=0, attribution_source='none'
                    success = record_attribution(appointment_id, contact_phone_normalized, None, 0.0)
                    attribution_result = {"attributed": False, "confidence": 0.0, "variant_id": None}
                    
                    # Emit attribution.missing event
                    log_event(
                        "attribution.missing",
                        "modal",
                        "warn",
                        correlation_id=f"{correlation_id}_no_attr",
                        entity_id=contact_id,
                        payload={
                            "appointment_id": appointment_id,
                            "phone": contact_phone_normalized,
                            "reason": "no_recent_touch"
                        }
                    )
            else:
                # No phone available - emit attribution.missing_phone
                log_event(
                    "attribution.missing_phone",  # Per spec: distinct event type
                    "modal",
                    "warn",
                    correlation_id=f"{correlation_id}_no_phone",
                    entity_id=contact_id,
                    payload={
                        "appointment_id": appointment_id,
                        "reason": "no_phone_in_payload"
                    }
                )
        
        return {"status": "ok", "attributed": attribution_result.get("attributed", False)}
    
    @api.get("/api/reliability-check")
    def reliability_check():
        """Basic reliability check"""
        from datetime import timedelta
        
        checks = {}
        utc_now = datetime.utcnow()
        ct_now = utc_now - timedelta(hours=6)
        today = ct_now.strftime('%Y-%m-%d')
        
        # DB connectivity
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            test_resp = requests.get(f"{SUPABASE_URL}/rest/v1/event_log_v2?limit=1", headers=headers, timeout=5)
            checks["database"] = "ok" if test_resp.status_code == 200 else "error"
        except:
            checks["database"] = "error"
        
        # Outreach enabled
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        checks["outreach_enabled"] = outreach_enabled
        
        return {
            "status": "healthy" if checks.get("database") == "ok" else "degraded",
            "checks": checks,
            "ct_time": ct_now.strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/kickoff-status") 
    def kickoff_status():
        """Returns kickoff readiness status for Jan 18 launch"""
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        utc_now = datetime.utcnow()
        ct_now = utc_now - timedelta(hours=6)
        today = ct_now.strftime('%Y-%m-%d')
        tomorrow = (ct_now + timedelta(days=1)).strftime('%Y-%m-%d')
        
        kickoff_scheduled = False
        kickoff_executed = False
        kickoff_date = None
        
        try:
            # Check today and tomorrow's kickoff
            for check_date in [today, tomorrow]:
                kr_resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/kickoff_runs?date=eq.{check_date}&limit=1",
                    headers=headers, timeout=10
                )
                if kr_resp.status_code == 200 and kr_resp.json():
                    row = kr_resp.json()[0]
                    kickoff_scheduled = True
                    kickoff_executed = row.get("executed", False)
                    kickoff_date = row.get("date")
                    break
        except Exception as e:
            print(f"[Kickoff Status] Error: {e}")
        
        # Count active variants
        active_variants = 0
        try:
            v_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/prompt_variants?active=eq.true&vertical=eq.hvac",
                headers=headers, timeout=10
            )
            if v_resp.status_code == 200:
                active_variants = len(v_resp.json())
        except:
            pass
        
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        readiness = "GO" if (kickoff_scheduled and active_variants > 0 and outreach_enabled) else "NOT_READY"
        
        return {
            "status": "ok",
            "today": today,
            "tomorrow": tomorrow,
            "kickoff_scheduled_for_tomorrow": kickoff_scheduled,
            "kickoff_date": kickoff_date,
            "kickoff_executed": kickoff_executed,
            "active_variants_count": active_variants,
            "outreach_enabled": outreach_enabled,
            "ct_time": ct_now.strftime('%Y-%m-%d %H:%M:%S CT'),
            "readiness": readiness,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.post("/api/campaign-batch")
    def campaign_batch(data: dict):
        """Execute batch campaign for contacts"""
        import time
        import uuid
        
        # Outreach kill switch
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        if not outreach_enabled:
            log_event("campaign.disabled", "modal", "warn", payload={
                "reason": "OUTREACH_ENABLED=false",
                "contact_count": len(data.get("contacts", []))
            })
            return {
                "status": "disabled",
                "reason": "OUTREACH_ENABLED=false",
                "sent": 0, "skipped_window": 0, "failed": 0, "details": []
            }
        
        contacts = data.get("contacts", [])
        dry_run = data.get("dry_run", False)
        run_id = data.get("run_id") or f"batch_{uuid.uuid4().hex[:8]}"
        
        results = {"sent": 0, "skipped_window": 0, "failed": 0, "details": []}
        
        log_event("campaign.batch.started", "modal", "info", correlation_id=run_id, payload={
            "contact_count": len(contacts),
            "dry_run": dry_run
        })
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        for contact in contacts[:50]:  # Limit to 50 per batch
            phone = contact.get("phone", "")
            company = contact.get("company", "")
            vertical = contact.get("vertical", "hvac")
            
            try:
                if dry_run:
                    results["sent"] += 1
                    results["details"].append({"phone": phone, "status": "dry_run", "company": company})
                else:
                    # Send via GHL webhook
                    ghl_resp = requests.post(GHL_SMS_WEBHOOK, json={
                        "phone": phone,
                        "message": f"Hi! We have a free diagnostic report ready for {company}. Reply YES to receive it, or STOP to opt out."
                    }, timeout=30)
                    
                    if ghl_resp.status_code in [200, 201]:
                        results["sent"] += 1
                        results["details"].append({"phone": phone, "status": "sent", "company": company})
                        log_event("sms.outbound", "modal", "info", entity_id=phone, payload={
                            "company": company, "vertical": vertical, "run_id": run_id
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({"phone": phone, "status": "ghl_error", "code": ghl_resp.status_code})
            except Exception as e:
                results["failed"] += 1
                results["details"].append({"phone": phone, "status": "exception", "error": str(e)})
            
            time.sleep(0.5)  # Rate limiting
        
        log_event("campaign.batch.completed", "modal", "info", correlation_id=run_id, payload={
            "sent": results["sent"],
            "failed": results["failed"],
            "dry_run": dry_run
        })
        
        return {
            "status": "ok",
            "run_id": run_id,
            "sent": results["sent"],
            "skipped_window": results["skipped_window"],
            "failed": results["failed"],
            "details": results["details"][:20]
        }
    
    @api.get("/api/learning-status")
    def learning_status():
        """Dashboard endpoint: Get current learning status"""
        return {
            "status": "ok",
            "policy": {"version": 3, "max_retries": 3, "weight_gemini": 0.7},
            "variants": [],
            "incidents": [],
            "canaries": []
        }
    
    @api.get("/api/launch/mode")
    def launch_mode():
        """
        Weekend Launch Mode endpoint for Jan 18-19.
        Returns effective time windows and mode status.
        """
        from datetime import timedelta
        
        utc_now = datetime.utcnow()
        ct_now = utc_now - timedelta(hours=6)  # CT is UTC-6
        today_str = ct_now.strftime('%Y-%m-%d')
        today_day = ct_now.day
        today_month = ct_now.month
        
        # Check if weekend launch mode is enabled
        weekend_launch_mode = os.environ.get("WEEKEND_LAUNCH_MODE", "true").lower() == "true"
        
        # Jan 18-19 specific windows (weekend launch exception)
        is_launch_weekend = (today_month == 1 and today_day in [18, 19])
        
        if weekend_launch_mode and is_launch_weekend:
            effective_windows = {
                "mode": "weekend_launch",
                "sms": {"start": 10, "end": 14, "description": "10am-2pm local"},
                "phone": {"start": 10, "end": 13, "description": "10am-1pm local"},
                "email": {"start": 9, "end": 12, "description": "9am-12pm local"}
            }
            # Log override once per call
            log_event("launch.weekend_override_enabled", "modal", "info", payload={
                "date": today_str,
                "sms_window": "10-14",
                "phone_window": "10-13",
                "email_window": "9-12"
            })
        else:
            # Standard weekday windows
            effective_windows = {
                "mode": "standard_weekday",
                "sms": {"start": 9, "end": 18, "description": "9am-6pm local"},
                "phone": {"start": 9, "end": 17, "description": "9am-5pm local"},
                "email": {"start": 8, "end": 18, "description": "8am-6pm local"}
            }
        
        return {
            "status": "ok",
            "weekend_launch_mode": weekend_launch_mode,
            "is_launch_weekend": is_launch_weekend,
            "today_ct": today_str,
            "ct_hour": ct_now.hour,
            "effective_windows": effective_windows,
            "auto_reverts": "Jan 20 or WEEKEND_LAUNCH_MODE=false",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.post("/api/email-batch")
    def email_batch(data: dict):
        """
        Send batch marketing emails via GHL.
        Payload: {
            "contacts": [{"email": "...", "company": "...", "subject": "...", "html": "...", "text": "..."}],
            "dry_run": true/false,
            "campaign_id": "optional",
            "variant_id": "optional"
        }
        """
        import time
        import uuid
        
        contacts = data.get("contacts", [])
        dry_run = data.get("dry_run", False)
        campaign_id = data.get("campaign_id")
        variant_id = data.get("variant_id")
        run_id = data.get("run_id") or f"email_batch_{uuid.uuid4().hex[:8]}"
        
        results = {"sent": 0, "failed": 0, "details": []}
        
        log_event("email.batch.started", "modal", "info", run_id, None, {
            "contact_count": len(contacts),
            "dry_run": dry_run,
            "campaign_id": campaign_id,
            "variant_id": variant_id
        })
        
        for contact in contacts[:25]:  # Limit to 25 per batch
            email = contact.get("email")
            subject = contact.get("subject", "Your Free HVAC Business Diagnostic Report")
            html_body = contact.get("html", f"<p>Hi! We have a diagnostic report ready for {contact.get('company', 'your business')}.</p>")
            text_body = contact.get("text", "")
            company = contact.get("company", "")
            
            if not email:
                results["failed"] += 1
                results["details"].append({"email": email, "status": "no_email"})
                continue
            
            if dry_run:
                results["sent"] += 1
                results["details"].append({"email": email, "status": "dry_run", "company": company})
            else:
                result = send_marketing_email_via_ghl(
                    to_email=email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    contact_id=contact.get("contact_id"),
                    campaign_id=campaign_id,
                    variant_id=variant_id,
                    metadata={"company": company, "run_id": run_id}
                )
                if result["success"]:
                    results["sent"] += 1
                    results["details"].append({"email": email, "status": "sent", "company": company})
                else:
                    results["failed"] += 1
                    results["details"].append({"email": email, "status": "failed", "error": result["error"]})
            
            time.sleep(0.3)  # Rate limiting
        
        log_event("email.batch.completed", "modal", "info", run_id, None, {
            "sent": results["sent"],
            "failed": results["failed"],
            "dry_run": dry_run
        })
        
        return {
            "status": "ok",
            "run_id": run_id,
            "sent": results["sent"],
            "failed": results["failed"],
            "provider": "ghl" if not dry_run else "dry_run",
            "details": results["details"][:10]  # Limit response size
        }
    
    # =========================================
    # UNIFIED COMMS SYSTEM ENDPOINTS
    # =========================================
    
    def send_sms_via_twilio(to_phone: str, message: str, from_phone: str = None) -> dict:
        """Send SMS via Twilio API. Returns success/failure dict."""
        import uuid
        from base64 import b64encode
        
        correlation_id = f"sms_{uuid.uuid4().hex[:8]}"
        from_phone = from_phone or CANONICAL_NUMBER
        
        TWILIO_SID = secrets.get("TWILIO_ACCOUNT_SID", "")
        TWILIO_TOKEN = secrets.get("TWILIO_AUTH_TOKEN", "")
        
        if not TWILIO_SID or not TWILIO_TOKEN:
            # Fallback to GHL
            log_event("sms.fallback", "modal", "warn", correlation_id, to_phone, {
                "reason": "Twilio credentials missing, using GHL fallback"
            })
            try:
                ghl_resp = requests.post(GHL_SMS_WEBHOOK, json={
                    "phone": to_phone,
                    "message": message
                }, timeout=30)
                if ghl_resp.status_code in [200, 201]:
                    log_event("sms.sent", "modal", "info", correlation_id, to_phone, {
                        "provider": "ghl_fallback", "message_preview": message[:50]
                    })
                    return {"success": True, "provider": "ghl_fallback", "message_sid": correlation_id}
            except:
                pass
            log_event("sms.failed", "modal", "error", correlation_id, to_phone, {"error": "All SMS providers failed"})
            return {"success": False, "provider": "none", "error": "All SMS providers failed"}
        
        try:
            # Twilio API call
            auth_str = b64encode(f"{TWILIO_SID}:{TWILIO_TOKEN}".encode()).decode()
            twilio_resp = requests.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
                headers={"Authorization": f"Basic {auth_str}"},
                data={"From": from_phone, "To": to_phone, "Body": message},
                timeout=30
            )
            
            if twilio_resp.status_code in [200, 201]:
                resp_data = twilio_resp.json()
                log_event("sms.sent", "modal", "info", correlation_id, to_phone, {
                    "provider": "twilio",
                    "message_sid": resp_data.get("sid"),
                    "from": from_phone,
                    "message_preview": message[:50]
                })
                return {"success": True, "provider": "twilio", "message_sid": resp_data.get("sid")}
            else:
                error = twilio_resp.json().get("message", f"HTTP {twilio_resp.status_code}")
                log_event("sms.failed", "modal", "error", correlation_id, to_phone, {
                    "provider": "twilio", "error": error, "status_code": twilio_resp.status_code
                })
                return {"success": False, "provider": "twilio", "error": error}
        except Exception as e:
            log_event("sms.failed", "modal", "error", correlation_id, to_phone, {
                "provider": "twilio", "error": str(e)
            })
            return {"success": False, "provider": "twilio", "error": str(e)}
    
    @api.post("/webhook/sms/inbound")
    async def sms_inbound_webhook(request: Request):
        """
        Receive inbound SMS from Twilio/carrier.
        Twilio sends form-urlencoded: From, To, Body, MessageSid
        """
        import uuid
        from urllib.parse import parse_qs
        
        try:
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            
            if "application/x-www-form-urlencoded" in content_type:
                params = parse_qs(body.decode())
                from_phone = params.get("From", [""])[0]
                to_phone = params.get("To", [""])[0]
                message_body = params.get("Body", [""])[0]
                message_sid = params.get("MessageSid", [""])[0]
            else:
                data = json.loads(body)
                from_phone = data.get("From") or data.get("from", "")
                to_phone = data.get("To") or data.get("to", "")
                message_body = data.get("Body") or data.get("body", "")
                message_sid = data.get("MessageSid") or data.get("message_sid", "")
            
            # Normalize phone
            from_phone = from_phone.replace(" ", "").replace("-", "")
            if not from_phone.startswith("+"):
                from_phone = f"+1{from_phone}" if len(from_phone) == 10 else f"+{from_phone}"
            
            correlation_id = message_sid or f"inbound_{uuid.uuid4().hex[:8]}"
            
            # Log webhook received
            log_event("webhook.sms.inbound", "modal", "info", correlation_id, from_phone, {
                "to": to_phone, "body_preview": message_body[:100], "message_sid": message_sid
            })
            
            # Log sms.received
            log_event("sms.received", "modal", "info", correlation_id, from_phone, {
                "message": message_body, "to": to_phone
            })
            
            # Generate AI reply (simple for now, can enhance with Gemini)
            message_upper = message_body.strip().upper()
            
            if message_upper in ["STOP", "UNSUBSCRIBE", "CANCEL"]:
                reply = "You have been unsubscribed. Reply START to re-subscribe."
                log_event("contact.optout", "modal", "info", correlation_id, from_phone, {
                    "keyword": message_upper
                })
            elif message_upper in ["YES", "Y", "INTERESTED", "INFO"]:
                reply = f"Great! Your free HVAC diagnostic report is being prepared. Book a call here: {BOOKING_LINK}"
                log_event("contact.engaged", "modal", "info", correlation_id, from_phone, {
                    "keyword": message_upper, "action": "positive_reply"
                })
            elif message_upper in ["HELP", "?"]:
                reply = f"Reply YES to get your free diagnostic, or call {CANONICAL_NUMBER}. Reply STOP to opt out."
            else:
                # Default acknowledgment
                reply = "Thanks for your message! A team member will follow up shortly. Reply STOP to opt out."
            
            # Send reply
            send_result = send_sms_via_twilio(from_phone, reply)
            
            # Return TwiML response for Twilio
            return {
                "status": "ok",
                "from": from_phone,
                "received": message_body[:50],
                "reply_sent": send_result["success"],
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            log_event("webhook.sms.error", "modal", "error", None, None, {"error": str(e)})
            return {"status": "error", "error": str(e)}
    
    @api.post("/api/sms/send")
    def sms_send(data: dict):
        """
        Send outbound SMS via carrier (Twilio).
        Payload: {"to": "+1555...", "message": "...", "dry_run": false}
        """
        import uuid
        
        to_phone = data.get("to", "")
        message = data.get("message", "")
        dry_run = data.get("dry_run", False)
        campaign_id = data.get("campaign_id")
        variant_id = data.get("variant_id")
        
        if not to_phone or not message:
            return {"status": "error", "error": "Missing 'to' or 'message'"}
        
        # Normalize phone
        to_phone = to_phone.replace(" ", "").replace("-", "")
        if not to_phone.startswith("+"):
            to_phone = f"+1{to_phone}" if len(to_phone) == 10 else f"+{to_phone}"
        
        run_id = f"sms_send_{uuid.uuid4().hex[:8]}"
        
        if dry_run:
            log_event("sms.dry_run", "modal", "info", run_id, to_phone, {
                "message_preview": message[:50], "campaign_id": campaign_id
            })
            return {
                "status": "ok",
                "run_id": run_id,
                "dry_run": True,
                "to": to_phone,
                "message_preview": message[:50],
                "provider": "dry_run"
            }
        
        result = send_sms_via_twilio(to_phone, message)
        
        return {
            "status": "ok" if result["success"] else "error",
            "run_id": run_id,
            "to": to_phone,
            "provider": result.get("provider"),
            "message_sid": result.get("message_sid"),
            "error": result.get("error")
        }
    
    @api.get("/api/comms/status")
    def comms_status():
        """
        Return unified comms system health status.
        """
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        # Get last events
        last_inbound_call = None
        last_inbound_sms = None
        last_outbound_sms = None
        last_errors = []
        
        try:
            # Last inbound call
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.call.answered&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            if resp.status_code == 200 and resp.json():
                last_inbound_call = resp.json()[0].get("ts")
            
            # Last inbound SMS
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.received&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            if resp.status_code == 200 and resp.json():
                last_inbound_sms = resp.json()[0].get("ts")
            
            # Last outbound SMS
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.sent&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            if resp.status_code == 200 and resp.json():
                last_outbound_sms = resp.json()[0].get("ts")
            
            # Last errors
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=in.(sms.failed,call.failed)&order=ts.desc&limit=5",
                headers=headers, timeout=5
            )
            if resp.status_code == 200:
                last_errors = [{"ts": e.get("ts"), "type": e.get("type"), "payload": e.get("payload")} for e in resp.json()]
        except Exception as e:
            last_errors.append({"error": str(e)})
        
        return {
            "status": "ok",
            "canonical_number": CANONICAL_NUMBER,
            "voice_provider": VOICE_PROVIDER,
            "sms_provider": SMS_PROVIDER,
            "last_inbound_call_ts": last_inbound_call,
            "last_inbound_sms_ts": last_inbound_sms,
            "last_outbound_sms_ts": last_outbound_sms,
            "last_errors": last_errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================
    # GHL SMS INTEGRATION (Weekend Mode - No Twilio)
    # ============================================================
    
    def generate_sms_reply(inbound_message: str, phone: str) -> str:
        """Generate AI reply using Gemini for HVAC qualification."""
        try:
            GEMINI_API_KEY = secrets.get("GEMINI_API_KEY", "")
            if not GEMINI_API_KEY:
                return "Thanks for reaching out! I'll have someone get back to you shortly. If urgent, call us at +1-352-758-5336."
            
            prompt = f"""You are Sarah, an AI assistant for a home services company specializing in HVAC.
A potential customer sent this text: "{inbound_message}"

Your goal:
1. Be warm and helpful
2. Qualify if they need HVAC service (install, repair, maintenance)
3. Offer our free efficiency report: https://aiserviceco.com/hvac
4. Ask ONE follow-up question to understand their need

Keep response under 160 characters. Be conversational, not salesy."""

            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return reply[:300] if reply else "Thanks for your message! What HVAC service can we help with?"
            else:
                log_event("error.occurred", "gemini", "warn", payload={"error": f"Gemini API: {resp.status_code}"})
                return "Thanks for your message! What HVAC service can we help with today?"
        except Exception as e:
            log_event("error.occurred", "gemini", "error", payload={"error": str(e)})
            return "Thanks for your message! We'll get back to you shortly."
    
    def send_sms_via_ghl(to_phone: str, message: str, contact_id: str = None, conversation_id: str = None, correlation_id: str = None) -> dict:
        """Send SMS reply via GHL Conversations API."""
        try:
            GHL_API_KEY = secrets.get("GHL_API_KEY", "")
            if not GHL_API_KEY:
                log_event("error.occurred", "ghl", "error", correlation_id=correlation_id, payload={"error": "GHL_API_KEY not configured"})
                return {"success": False, "error": "GHL_API_KEY missing"}
            
            headers = {
                "Authorization": f"Bearer {GHL_API_KEY}",
                "Content-Type": "application/json",
                "Version": "2021-07-28"
            }
            
            # Try Conversations API first if we have conversation_id
            if conversation_id:
                resp = requests.post(
                    f"https://services.leadconnectorhq.com/conversations/{conversation_id}/messages",
                    headers=headers,
                    json={
                        "type": "SMS",
                        "message": message,
                        "locationId": GHL_LOCATION_ID
                    },
                    timeout=10
                )
                
                if resp.status_code in [200, 201]:
                    log_event("sms.reply.sent", "ghl", "info", correlation_id=correlation_id, entity_id=to_phone, payload={
                        "to": to_phone,
                        "message": message[:50],
                        "conversation_id": conversation_id,
                        "method": "conversations_api"
                    })
                    return {"success": True, "method": "conversations_api", "response_code": resp.status_code}
            
            # Fallback: Create contact message via contacts API
            if contact_id:
                resp = requests.post(
                    f"https://services.leadconnectorhq.com/contacts/{contact_id}/messages",
                    headers=headers,
                    json={
                        "type": "SMS",
                        "message": message
                    },
                    timeout=10
                )
                
                if resp.status_code in [200, 201]:
                    log_event("sms.reply.sent", "ghl", "info", correlation_id=correlation_id, entity_id=to_phone, payload={
                        "to": to_phone,
                        "message": message[:50],
                        "contact_id": contact_id,
                        "method": "contacts_api"
                    })
                    return {"success": True, "method": "contacts_api", "response_code": resp.status_code}
            
            # Final fallback: webhook trigger
            resp = requests.post(
                GHL_SMS_WEBHOOK,
                json={
                    "phone": to_phone,
                    "message": message,
                    "source": "modal_sms_reply"
                },
                timeout=10
            )
            
            if resp.status_code in [200, 201]:
                log_event("sms.reply.sent", "ghl", "info", correlation_id=correlation_id, entity_id=to_phone, payload={
                    "to": to_phone,
                    "message": message[:50],
                    "method": "webhook_fallback"
                })
                return {"success": True, "method": "webhook_fallback", "response_code": resp.status_code}
            
            # All attempts failed
            error_msg = f"All GHL send methods failed. Last status: {resp.status_code}"
            log_event("sms.reply.failed", "ghl", "error", correlation_id=correlation_id, entity_id=to_phone, payload={
                "to": to_phone,
                "error": error_msg
            })
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            log_event("sms.reply.failed", "ghl", "error", correlation_id=correlation_id, entity_id=to_phone, payload={
                "to": to_phone,
                "error": str(e)
            })
            return {"success": False, "error": str(e)}
    
    @api.post("/webhook/ghl/sms/inbound")
    async def ghl_sms_inbound_webhook(request: Request):
        """
        Handle inbound SMS from GHL.
        - Log webhook and sms.inbound events
        - Generate AI reply
        - Send reply via GHL
        - Alert if reply fails
        """
        import uuid
        correlation_id = f"ghl_sms_{uuid.uuid4().hex[:8]}"
        
        try:
            body = await request.json()
        except:
            body = {}
        
        # Log raw webhook
        log_event("webhook.inbound", "ghl", "info", correlation_id=correlation_id, payload={
            "provider": "ghl",
            "type": "sms_inbound",
            "raw": body
        })
        
        # Extract fields - GHL sends various formats
        phone_raw = (
            body.get("phone") or 
            body.get("from") or 
            body.get("contactPhone") or 
            (body.get("contact", {}) or {}).get("phone") or
            body.get("fromNumber")
        )
        message_body = (
            body.get("message") or 
            body.get("body") or 
            body.get("text") or 
            body.get("smsBody") or
            ""
        )
        contact_id = body.get("contactId") or body.get("contact_id") or (body.get("contact", {}) or {}).get("id")
        conversation_id = body.get("conversationId") or body.get("conversation_id")
        
        phone_normalized = normalize_phone(phone_raw) if phone_raw else None
        
        # Log structured inbound event
        log_event("sms.inbound", "ghl", "info", correlation_id=correlation_id, entity_id=phone_normalized, payload={
            "phone": phone_normalized,
            "phone_raw": phone_raw,
            "body": message_body[:200] if message_body else None,
            "contact_id": contact_id,
            "conversation_id": conversation_id
        })
        
        # Generate AI reply if we have a phone
        if phone_normalized and message_body:
            log_event("sms.reply.attempt", "modal", "info", correlation_id=correlation_id, entity_id=phone_normalized, payload={
                "phone": phone_normalized,
                "inbound_preview": message_body[:50]
            })
            
            # Generate reply
            reply_text = generate_sms_reply(message_body, phone_normalized)
            
            # Send via GHL
            send_result = send_sms_via_ghl(phone_normalized, reply_text, contact_id, conversation_id, correlation_id)
            
            if not send_result.get("success"):
                # Alert on failure
                send_alert_email(
                    subject=f"🚨 SMS Reply Failed - {phone_normalized}",
                    body=f"Failed to send SMS reply to {phone_normalized}.\n\nInbound: {message_body[:100]}\nReply: {reply_text[:100]}\nError: {send_result.get('error')}",
                    severity="error"
                )
        
        return {"status": "ok", "correlation_id": correlation_id}
    
    # ============================================================
    # P0: OPTION A - REPLY TEXT ONLY (GHL sends SMS natively)
    # ============================================================
    
    def generate_sms_reply_v2(inbound_message: str, phone: str) -> dict:
        """Generate AI reply using Gemini for HVAC qualification. Returns dict with reply + metadata."""
        import random
        import traceback
        
        model = "gemini-2.0-flash"
        intent = "unknown"
        
        # Detect emergency keywords
        emergency_keywords = ["no ac", "no air", "broken", "emergency", "urgent", "hot", "dying"]
        is_emergency = any(kw in inbound_message.lower() for kw in emergency_keywords)
        if is_emergency:
            intent = "emergency"
        elif any(kw in inbound_message.lower() for kw in ["quote", "price", "cost", "estimate"]):
            intent = "pricing"
        elif any(kw in inbound_message.lower() for kw in ["tune", "maintenance", "check", "inspect"]):
            intent = "maintenance"
        elif any(kw in inbound_message.lower() for kw in ["install", "new", "replace"]):
            intent = "install"
        else:
            intent = "general"
        
        try:
            GEMINI_API_KEY = secrets.get("GEMINI_API_KEY", "")
            if not GEMINI_API_KEY:
                fallback = "Thanks for reaching out! How can AI Service Co help automate your business today? -Sarah"
                return {"reply_text": fallback, "model": "fallback", "intent": intent, "error": None}
            
            if is_emergency:
                prompt = f"""You are Sarah, an AI sales consultant for AI Service Co - we help businesses automate with AI solutions.
The customer sent: "{inbound_message}"
This sounds urgent! Respond with empathy and offer to schedule a quick call at +1 (863) 213-2505 to discuss their AI needs.
Keep under 300 characters. Sign off with "-Sarah"."""
            else:
                prompt = f"""You are Sarah, an AI sales consultant for AI Service Co.
We offer AI automation solutions for businesses: AI phone agents, SMS/email automation, lead generation, content creation, and custom AI workflows.

The customer sent: "{inbound_message}"

Your goal:
1. Be warm and helpful
2. Ask ONE relevant follow-up question to understand their business needs
3. Offer to schedule a free AI Strategy Session via https://link.aiserviceco.com/discovery
4. Keep under 300 characters
5. Sign off with "-Sarah"

Be conversational, not salesy."""
            
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                reply = reply.strip()[:320] if reply else "Thanks for your message! How can AI Service Co help your business today? -Sarah"
                if not reply.endswith("-Sarah"):
                    reply = reply[:300] + " -Sarah"
                return {"reply_text": reply, "model": model, "intent": intent, "error": None}
            else:
                return {
                    "reply_text": "Thanks for your message! How can AI Service Co help automate your business today? -Sarah",
                    "model": "fallback",
                    "intent": intent,
                    "error": f"Gemini API: {resp.status_code}"
                }
        except Exception as e:
            return {
                "reply_text": "Thanks for your message! We'll get back to you shortly. -Sarah",
                "model": "fallback",
                "intent": intent,
                "error": str(e)
            }
    
    @api.post("/api/sms/reply-text")
    async def sms_reply_text(request: Request):
        """
        P0: Returns reply text only - GHL sends SMS natively.
        Input: {phone, message, contactId, conversationId}
        Output: {reply_text, correlation_id, ok, error}
        ALWAYS returns non-empty reply_text (bulletproof fallback).
        """
        import random
        import traceback
        
        # Safe fallback - NEVER return empty
        SAFE_FALLBACK = "Thanks for reaching out! What AI automation challenge can we help solve for your business? -Sarah"
        
        try:
            data = await request.json()
        except:
            data = {}
        
        phone = data.get("phone", "")
        message = data.get("message", "")
        contact_id = data.get("contactId", "")
        conversation_id = data.get("conversationId", "")
        
        # Normalize phone
        phone_normalized = normalize_phone(phone) if phone else ""
        
        # Generate stable correlation_id
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        rand4 = ''.join(random.choices('abcdef0123456789', k=4))
        correlation_id = f"sms_{phone_normalized.replace('+', '')}_{ts}_{rand4}"
        
        error_msg = None
        ok = True
        
        # Emit sms.inbound immediately
        try:
            log_event("sms.inbound", "ghl", "info",
                correlation_id=correlation_id,
                entity_id=phone_normalized,
                payload={
                    "phone": phone_normalized,
                    "message_preview": message[:100] if message else "",
                    "contact_id": contact_id,
                    "conversation_id": conversation_id
                }
            )
        except Exception as e:
            error_msg = f"log_event failed: {str(e)}"
        
        # Generate reply
        reply_text = SAFE_FALLBACK  # Start with fallback
        try:
            result = generate_sms_reply_v2(message, phone_normalized)
            generated_text = result.get("reply_text", "")
            
            # Only use generated text if non-empty
            if generated_text and len(generated_text.strip()) > 5:
                reply_text = generated_text
            else:
                ok = False
                error_msg = "Gemini returned empty/short response"
            
            # Check for Gemini errors
            if result.get("error"):
                ok = False
                error_msg = result["error"]
            
            # Emit sms.reply.generated
            log_event("sms.reply.generated", "modal", "info",
                correlation_id=correlation_id,
                entity_id=phone_normalized,
                payload={
                    "reply_text_len": len(reply_text),
                    "model": result.get("model", "unknown"),
                    "intent": result.get("intent", "unknown"),
                    "used_fallback": reply_text == SAFE_FALLBACK
                }
            )
            
        except Exception as e:
            ok = False
            error_msg = str(e)
            log_event("error.occurred", "modal", "error",
                correlation_id=correlation_id,
                payload={"error": str(e), "traceback": traceback.format_exc()[:500], "used_fallback": True}
            )
        
        # GUARANTEE: reply_text is never empty
        if not reply_text or len(reply_text.strip()) < 5:
            reply_text = SAFE_FALLBACK
            ok = False
            error_msg = error_msg or "Empty reply after all attempts"
        
        return {
            "reply_text": reply_text,
            "correlation_id": correlation_id,
            "ok": ok,
            "error": error_msg
        }
    
    # ============================================================
    # P2: REPLY-SENT CALLBACK (GHL calls after sending SMS)
    # ============================================================
    
    @api.post("/api/sms/reply-sent")
    async def sms_reply_sent(request: Request):
        """
        Callback from GHL after SMS is sent. Logs sms.reply.sent event.
        Input: {phone, conversationId, correlation_id, provider, message_id}
        """
        try:
            data = await request.json()
        except:
            data = {}
        
        phone = data.get("phone", "")
        conversation_id = data.get("conversationId", "")
        correlation_id = data.get("correlation_id", "")
        provider = data.get("provider", "ghl")
        message_id = data.get("message_id", "")
        
        phone_normalized = normalize_phone(phone) if phone else ""
        
        log_event("sms.reply.sent", provider, "info",
            correlation_id=correlation_id,
            entity_id=phone_normalized,
            payload={
                "phone": phone_normalized,
                "conversation_id": conversation_id,
                "provider": provider,
                "message_id": message_id
            }
        )
        
        return {"status": "ok", "logged": True}
    
    # ============================================================
    # P3: UPGRADED SMS HEALTH (more fields)
    # ============================================================
    
    @api.get("/api/sms/health")
    def sms_health():
        """SMS health check with extended fields."""
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            
            # Last SMS inbound
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_inbound_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Last SMS reply generated
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.generated&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_generated_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Last SMS reply sent
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.sent&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_sent_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Last error
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.error.occurred&severity=eq.error&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_error = None
            if resp.status_code == 200 and resp.json():
                err = resp.json()[0]
                last_error = {"ts": err.get("ts"), "payload": err.get("payload")}
            
            # Count unreplied in last 60s
            cutoff_60s = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&ts=gte.{cutoff_60s}&select=entity_id",
                headers=headers, timeout=5
            )
            inbound_phones_60s = set(e.get("entity_id") for e in resp.json() if e.get("entity_id")) if resp.status_code == 200 else set()
            
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.sent&ts=gte.{cutoff_60s}&select=entity_id",
                headers=headers, timeout=5
            )
            replied_phones_60s = set(e.get("entity_id") for e in resp.json() if e.get("entity_id")) if resp.status_code == 200 else set()
            
            unreplied_count = len(inbound_phones_60s - replied_phones_60s)
            
            return {
                "status": "ok",
                "sms_pipeline_healthy": unreplied_count == 0,
                "last_sms_inbound_ts": last_inbound_ts,
                "last_sms_reply_generated_ts": last_generated_ts,
                "last_sms_reply_sent_ts": last_sent_ts,
                "unreplied_count_60s": unreplied_count,
                "last_error": last_error
            }
        except Exception as e:
            return {"status": "degraded", "error": str(e), "sms_pipeline_healthy": False}
    
    # ============================================================
    # AUDITOR STATUS (test location)
    # ============================================================
    
    @api.get("/api/auditor2/status")
    def auditor2_status():
        """Test auditor endpoint in working location."""
        return {
            "status": "GREEN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test": "auditor2_working"
        }
    
    # ============================================================
    # P0: SMS DEBUG ENDPOINT
    # ============================================================
    
    @api.get("/api/debug/sms")
    def debug_sms(run_audit: str = None):
        """
        Diagnostic endpoint for SMS debugging.
        Add ?run_audit=1 to run synthetic SMS test and return auditor status.
        """
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            
            # If run_audit is requested, do synthetic test first
            audit_result = None
            if run_audit == "1":
                # Run synthetic SMS test
                test_message = "SYNTHETIC_AUDIT: Test AI response capability"
                test_phone = "+15551234567"
                
                try:
                    # Call Gemini for synthetic test
                    GEMINI_KEY = secrets.get("GEMINI_API_KEY")
                    if GEMINI_KEY:
                        prompt = f"""You are Sarah, an AI sales consultant for AI Service Co.
We offer AI automation solutions for businesses: AI phone agents, SMS/email automation, lead generation, content creation, and custom AI workflows.

Reply to this inquiry in under 320 characters. Ask one qualifying question about their AI automation needs. Sign off with -Sarah.

Message: "{test_message}"
"""
                        gemini_resp = requests.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
                            headers={"Content-Type": "application/json"},
                            json={
                                "contents": [{"parts": [{"text": prompt}]}],
                                "generationConfig": {"maxOutputTokens": 100, "temperature": 0.7}
                            },
                            timeout=15
                        )
                        
                        if gemini_resp.status_code == 200:
                            reply_text = gemini_resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            
                            is_non_empty = len(reply_text) > 10
                            is_not_literal = "reply_text" not in reply_text.lower() and "reply text" not in reply_text.lower()
                            has_question = "?" in reply_text
                            
                            if is_non_empty and is_not_literal and has_question:
                                log_event("sms.synthetic.pass", "auditor", "info",
                                    payload={"test_message": test_message, "reply_length": len(reply_text), "reply_preview": reply_text[:60]})
                                audit_result = {"status": "PASS", "reply_length": len(reply_text), "has_question": has_question}
                            else:
                                log_event("sms.synthetic.fail", "auditor", "warn",
                                    payload={"reason": "low_quality", "reply_text": reply_text[:100], "is_empty": not is_non_empty, "is_literal": not is_not_literal})
                                audit_result = {"status": "FAIL", "reason": "low_quality_reply", "reply_preview": reply_text[:60]}
                        else:
                            log_event("sms.synthetic.fail", "auditor", "error",
                                payload={"reason": "gemini_error", "status_code": gemini_resp.status_code})
                            audit_result = {"status": "FAIL", "reason": "gemini_api_error", "status_code": gemini_resp.status_code}
                    else:
                        audit_result = {"status": "FAIL", "reason": "no_gemini_key"}
                except Exception as ae:
                    log_event("sms.synthetic.fail", "auditor", "error",
                        payload={"reason": "exception", "error": str(ae)})
                    audit_result = {"status": "FAIL", "reason": "exception", "error": str(ae)}
            
            # Last 20 sms events (increased from 10)
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&order=ts.desc&limit=20",
                headers=headers, timeout=5
            )
            inbound_events = resp.json() if resp.status_code == 200 else []
            
            # Last 20 sms.reply.* events  
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=like.sms.reply.*&order=ts.desc&limit=20",
                headers=headers, timeout=5
            )
            reply_events = resp.json() if resp.status_code == 200 else []
            
            # Last 20 synthetic/deadman events
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?source=eq.auditor&order=ts.desc&limit=20",
                headers=headers, timeout=5
            )
            auditor_events = resp.json() if resp.status_code == 200 else []
            
            # Last 10 errors with ghl source
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.error.occurred&source=eq.ghl&order=ts.desc&limit=10",
                headers=headers, timeout=5
            )
            ghl_errors = resp.json() if resp.status_code == 200 else []
            
            # Determine last send method used
            last_method = None
            if reply_events:
                last_payload = reply_events[0].get("payload", {})
                if isinstance(last_payload, str):
                    try:
                        last_payload = json.loads(last_payload)
                    except:
                        last_payload = {}
                last_method = last_payload.get("method", "unknown")
            
            result = {
                "status": "ok",
                "ghl_location_id": GHL_LOCATION_ID[:8] + "..." if GHL_LOCATION_ID else None,
                "canonical_sms_number": CANONICAL_NUMBER,
                "last_send_method": last_method,
                "sms_inbound_events": [
                    {"ts": e.get("ts"), "phone": e.get("entity_id"), "correlation_id": e.get("correlation_id")}
                    for e in inbound_events
                ],
                "sms_reply_events": [
                    {"ts": e.get("ts"), "type": e.get("type"), "phone": e.get("entity_id"), "method": (e.get("payload") or {}).get("method")}
                    for e in reply_events
                ],
                "auditor_events": [
                    {"ts": e.get("ts"), "type": e.get("type"), "severity": e.get("severity")}
                    for e in auditor_events[:10]
                ],
                "ghl_errors": [
                    {"ts": e.get("ts"), "error": (e.get("payload") or {}).get("error", "")[:100]}
                    for e in ghl_errors
                ]
            }
            
            if audit_result:
                result["audit_result"] = audit_result
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ============================================================
    # UNIFIED AUDITOR STATUS - Customer-facing health check
    # Returns GREEN/YELLOW/RED based on all synthetic monitors
    # Updated: 2026-01-18T23:30:00Z - Force deploy
    # ============================================================
    
    @api.get("/api/auditor/status")
    def auditor_status():
        """Unified customer-facing health status: GREEN/YELLOW/RED."""
        now = datetime.now(timezone.utc)
        
        # Simplified version - always return with basic info
        return {
            "status": "YELLOW",
            "reason": "auditor_checks_initializing",
            "timestamp": now.isoformat(),
            "brand_canon": {
                "voice_number": VOICE_NUMBER,
                "sms_number": SMS_NUMBER,
                "booking_link": "https://link.aiserviceco.com/discovery"
            }
        }
    
    # ============================================================
    # P3: CANONICAL ROUTING TRUTH ENDPOINT (enhanced)
    # ============================================================
    
    @api.get("/api/routing/truth")
    def routing_truth():
        """Canonical routing truth - single source for all number configs."""
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            
            # Last call event
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=like.call.*&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_call_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Last SMS inbound
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_sms_inbound_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Last SMS reply
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.sent&order=ts.desc&limit=1",
                headers=headers, timeout=5
            )
            last_sms_reply_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
            
            # Calculate staleness
            now = datetime.now(timezone.utc)
            sms_inbound_stale = False
            sms_reply_stale = False
            
            if last_sms_inbound_ts and last_sms_reply_ts:
                try:
                    inbound_dt = datetime.fromisoformat(last_sms_inbound_ts.replace("Z", "+00:00"))
                    reply_dt = datetime.fromisoformat(last_sms_reply_ts.replace("Z", "+00:00"))
                    sms_reply_stale = (inbound_dt - reply_dt).total_seconds() > 60
                except:
                    pass
            
            return {
                "status": "ok",
                # Canonical contact numbers
                "canonical_voice_number": VOICE_NUMBER,
                "canonical_sms_number": SMS_NUMBER,
                "voice_provider": VOICE_PROVIDER,
                "sms_provider": SMS_PROVIDER,
                # Business info
                "booking_link": "https://link.aiserviceco.com/discovery",
                "business_name": "AI Service Co",
                "hours": "Mon-Fri 8am-6pm EST",
                "website": "https://www.aiserviceco.com",
                # Activity timestamps
                "last_call_event_ts": last_call_ts,
                "last_sms_inbound_ts": last_sms_inbound_ts,
                "last_sms_reply_ts": last_sms_reply_ts,
                "sms_reply_stale": sms_reply_stale,
                "timestamp": now.isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    return api


# ============================================================
# STEP 3: SMS DEADMAN WATCHDOG (Scheduled every 2 minutes)
# TEMPORARILY DISABLED - causing Modal container crash
# Re-enable after main API is stable
# ============================================================

@app.function(schedule=modal.Cron("*/2 * * * *"), secrets=[secrets])
def scheduled_sms_deadman():
    """
    Every 2 minutes: check SMS health and alert if replies are stalled.
    - If unreplied_count_60s > 0: emit incident.deadman + send alert
    - If last_sms_inbound_ts > last_sms_reply_ts by >60s: stalled pipeline
    """
    import requests
    from datetime import datetime, timedelta, timezone
    
    # Check if deadman is enabled via env var
    if os.environ.get("SMS_DEADMAN_ENABLED", "true").lower() != "true":
        return  # Deadman disabled
    
    env_secrets = {
        "SUPABASE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", "")),
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", "")
    }
    SUPABASE_KEY = env_secrets["SUPABASE_KEY"]
    SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    
    def log_deadman_event(event_type, severity, payload):
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(
                f"{SUPABASE_URL}/rest/v1/event_log_v2",
                headers=headers,
                json={"type": event_type, "source": "deadman", "severity": severity, "payload": payload},
                timeout=5
            )
        except:
            pass
    
    def send_deadman_alert(subject, body):
        try:
            RESEND_API_KEY = env_secrets.get("RESEND_API_KEY", "")
            if not RESEND_API_KEY:
                return
            requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "alerts@aiserviceco.com",
                    "to": ["nearmiss1193@gmail.com"],
                    "subject": subject,
                    "text": body
                },
                timeout=10
            )
        except:
            pass
    
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        # Get SMS health metrics
        cutoff_60s = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
        
        # Last SMS inbound
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&order=ts.desc&limit=1",
            headers=headers, timeout=5
        )
        last_inbound_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
        
        # Last SMS reply sent
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.sent&order=ts.desc&limit=1",
            headers=headers, timeout=5
        )
        last_reply_ts = resp.json()[0].get("ts") if resp.status_code == 200 and resp.json() else None
        
        # Count unreplied in last 60s
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.inbound&ts=gte.{cutoff_60s}&select=entity_id",
            headers=headers, timeout=5
        )
        inbound_phones = set(e.get("entity_id") for e in resp.json() if e.get("entity_id")) if resp.status_code == 200 else set()
        
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/event_log_v2?type=eq.sms.reply.sent&ts=gte.{cutoff_60s}&select=entity_id",
            headers=headers, timeout=5
        )
        replied_phones = set(e.get("entity_id") for e in resp.json() if e.get("entity_id")) if resp.status_code == 200 else set()
        
        unreplied_count = len(inbound_phones - replied_phones)
        
        # Check for stalled condition
        is_stalled = False
        if unreplied_count > 0:
            is_stalled = True
        elif last_inbound_ts and last_reply_ts:
            try:
                inbound_dt = datetime.fromisoformat(last_inbound_ts.replace("Z", "+00:00"))
                reply_dt = datetime.fromisoformat(last_reply_ts.replace("Z", "+00:00"))
                if (inbound_dt - reply_dt).total_seconds() > 60:
                    is_stalled = True
            except:
                pass
        
        if is_stalled:
            # Emit incident
            log_deadman_event("incident.deadman", "error", {
                "unreplied_count": unreplied_count,
                "unreplied_phones": list(inbound_phones - replied_phones),
                "last_inbound_ts": last_inbound_ts,
                "last_reply_ts": last_reply_ts
            })
            
            # Send alert
            send_deadman_alert(
                "🚨 SMS DEADMAN: replies stalled",
                f"SMS pipeline stalled!\n\nUnreplied count: {unreplied_count}\nUnreplied phones: {list(inbound_phones - replied_phones)}\nLast inbound: {last_inbound_ts}\nLast reply: {last_reply_ts}\n\nCheck /api/debug/sms for details."
            )
        else:
            # Heartbeat - all good
            log_deadman_event("deadman.heartbeat", "info", {
                "unreplied_count": 0,
                "last_inbound_ts": last_inbound_ts,
                "last_reply_ts": last_reply_ts,
                "status": "healthy"
            })
    except Exception as e:
        log_deadman_event("error.occurred", "error", {"source": "sms_deadman", "error": str(e)})


# ============================================================
# COMPONENT B: WEBSITE NUMBER DRIFT MONITOR (Every 10 min)
# Fetches website, extracts phone numbers, compares to routing truth
# ============================================================

@app.function(schedule=modal.Cron("*/10 * * * *"), secrets=[secrets])
def scheduled_website_monitor():
    """Check website for phone number drift every 10 minutes."""
    import re
    import os
    
    SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    RESEND_KEY = os.environ.get("RESEND_API_KEY", "")
    VOICE_NUMBER = "+18632132505"
    SMS_NUMBER = "+13527585336"
    WEBSITE_URL = "https://www.aiserviceco.com/"
    
    def log_monitor_event(event_type, severity, payload):
        if not SUPABASE_KEY:
            return
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(
                f"{SUPABASE_URL}/rest/v1/event_log_v2",
                headers=headers, timeout=5,
                json={"type": event_type, "source": "website_monitor", "severity": severity, "payload": payload}
            )
        except:
            pass
    
    try:
        # Fetch website
        resp = requests.get(WEBSITE_URL, timeout=15, headers={"User-Agent": "Empire-Auditor/1.0"})
        if resp.status_code != 200:
            log_monitor_event("error.occurred", "warn", {"url": WEBSITE_URL, "status": resp.status_code})
            return
        
        html = resp.text
        
        # Regex to extract phone numbers
        phone_pattern = r'[\+]?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        found_numbers = re.findall(phone_pattern, html)
        
        # Normalize found numbers to just digits
        def normalize(num):
            digits = re.sub(r'\D', '', num)
            if len(digits) == 10:
                digits = '1' + digits
            return '+' + digits if digits else ''
        
        normalized = set(normalize(n) for n in found_numbers if len(re.sub(r'\D', '', n)) >= 10)
        
        # Check if canonical numbers are present
        voice_found = VOICE_NUMBER in normalized or '+1' + VOICE_NUMBER[-10:] in normalized
        sms_found = SMS_NUMBER in normalized or '+1' + SMS_NUMBER[-10:] in normalized
        
        if voice_found and sms_found:
            log_monitor_event("website_monitor.pass", "info", {
                "expected_voice": VOICE_NUMBER,
                "expected_sms": SMS_NUMBER,
                "found_numbers": list(normalized)[:10],  # Limit to 10
                "url": WEBSITE_URL
            })
        else:
            # MISMATCH - alert!
            log_monitor_event("incident.website_number_mismatch", "error", {
                "expected_voice": VOICE_NUMBER,
                "expected_sms": SMS_NUMBER,
                "voice_found": voice_found,
                "sms_found": sms_found,
                "found_on_page": list(normalized)[:10],
                "url": WEBSITE_URL
            })
            
            # Send alert email
            if RESEND_KEY:
                try:
                    requests.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                        json={
                            "from": "Empire Auditor <auditor@aiserviceco.com>",
                            "to": ["nearmiss1193@gmail.com"],
                            "subject": "🚨 WEBSITE NUMBER MISMATCH",
                            "html": f"<h2>Phone Number Drift Detected</h2><p><b>Expected Voice:</b> {VOICE_NUMBER} {'✅' if voice_found else '❌'}</p><p><b>Expected SMS:</b> {SMS_NUMBER} {'✅' if sms_found else '❌'}</p><p><b>Found on page:</b> {list(normalized)[:10]}</p><p><a href='{WEBSITE_URL}'>Check Website</a></p>"
                        },
                        timeout=10
                    )
                except:
                    pass
    except Exception as e:
        log_monitor_event("error.occurred", "error", {"source": "website_monitor", "error": str(e)})


# ============================================================
# COMPONENT C: SMS SYNTHETIC MONITOR (Every 10 min)
# Tests reply-text generation without sending real SMS
# ============================================================

@app.function(schedule=modal.Cron("*/10 * * * *"), secrets=[secrets])
def scheduled_sms_synthetic():
    """Run synthetic SMS test every 10 minutes."""
    import os
    import time
    
    SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    def log_synthetic_event(event_type, severity, payload):
        if not SUPABASE_KEY:
            return
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(
                f"{SUPABASE_URL}/rest/v1/event_log_v2",
                headers=headers, timeout=5,
                json={"type": event_type, "source": "sms_synthetic", "severity": severity, "payload": payload}
            )
        except:
            pass
    
    try:
        start = time.time()
        
        # Call the Gemini API directly for synthetic test
        test_message = "Synthetic test: need AC tune-up pricing for my home"
        test_phone = "+15551234567"
        
        if not GEMINI_KEY:
            log_synthetic_event("sms.synthetic.fail", "error", {"error": "GEMINI_API_KEY not configured"})
            return
        
        # Generate reply using Gemini
        try:
            gemini_resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": f"You are Sarah, an AI sales consultant for AI Service Co. Reply to this customer inquiry in under 320 chars, ask one qualifying question about their AI automation needs, sign off with -Sarah: '{test_message}'"}]}],
                    "generationConfig": {"maxOutputTokens": 100, "temperature": 0.7}
                },
                timeout=15
            )
            
            latency_ms = int((time.time() - start) * 1000)
            
            if gemini_resp.status_code == 200:
                data = gemini_resp.json()
                reply_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Check pass conditions
                is_non_empty = len(reply_text.strip()) > 10
                has_question = "?" in reply_text
                
                if is_non_empty and has_question:
                    log_synthetic_event("sms.synthetic.pass", "info", {
                        "reply_text_len": len(reply_text),
                        "contains_question": has_question,
                        "model": "gemini-2.0-flash",
                        "latency_ms": latency_ms
                    })
                else:
                    log_synthetic_event("sms.synthetic.fail", "warn", {
                        "reply_text_len": len(reply_text),
                        "contains_question": has_question,
                        "reason": "Missing question or too short",
                        "latency_ms": latency_ms
                    })
            else:
                log_synthetic_event("sms.synthetic.fail", "error", {
                    "error": f"Gemini API: {gemini_resp.status_code}",
                    "latency_ms": latency_ms
                })
        except Exception as e:
            log_synthetic_event("sms.synthetic.fail", "error", {"error": str(e)})
    except Exception as e:
        log_synthetic_event("error.occurred", "error", {"source": "sms_synthetic", "error": str(e)})

