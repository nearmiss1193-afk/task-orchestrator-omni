"""
SOVEREIGN ORCHESTRATOR - Stripped down for emergency recovery
Only essential endpoints, NO scheduled functions
"""
import modal
from fastapi import FastAPI, Request
from datetime import datetime
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

# Unified Comms System - Canonical Number
CANONICAL_NUMBER = "+13527585336"  # Single source of truth for all comms
SMS_PROVIDER = "twilio"  # "twilio" | "telnyx" | "ghl_fallback"
VOICE_PROVIDER = "vapi"

# Secrets loaded at runtime from modal.Secret
def get_secrets():
    return {
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", ""),
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
        
        # 4. Log this truth check (debug level)
        try:
            log_event("dashboard.truth_checked", "modal", "debug", 
                      correlation_id=f"truth_{uuid.uuid4().hex[:6]}",
                      payload={
                          "last_event_ts": result["last_event_ts"],
                          "last_kpi_ts": result["last_kpi_ts"],
                          "last_campaign_ran_at": result["last_campaign_ran_at"]
                      })
        except:
            pass
        
        return result
    
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
        Handle GHL appointment webhooks.
        Expected to be called by GHL workflow on appointment creation/update.
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
        
        # Extract contact info
        contact = body.get("contact", {})
        contact_id = body.get("contactId") or contact.get("id") or body.get("contact_id")
        
        log_event(
            mapped_type,
            "ghl",
            "info",
            correlation_id=f"appt_{uuid.uuid4().hex[:8]}",
            entity_id=contact_id,
            payload={
                "appointment_id": body.get("appointmentId") or body.get("appointment_id"),
                "calendar_id": body.get("calendarId") or body.get("calendar_id"),
                "contact_id": contact_id,
                "start_time": body.get("startTime") or body.get("start_time"),
                "end_time": body.get("endTime") or body.get("end_time"),
                "status": body.get("status"),
                "title": body.get("title"),
                "contact_name": contact.get("name") or body.get("contact_name"),
                "contact_phone": contact.get("phone") or body.get("phone"),
                "contact_email": contact.get("email") or body.get("email"),
                "location_id": body.get("locationId") or GHL_LOCATION_ID,
                "raw_type": ghl_type
            }
        )
        
        return {"status": "ok", "event_type": mapped_type, "contact_id": contact_id}
    
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
    
    return api
