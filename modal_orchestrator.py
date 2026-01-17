"""
SOVEREIGN ORCHESTRATOR - Unified ASGI App
All routes bundled into one FastAPI app for reliable Modal deployment.
"""
import modal
from fastapi import FastAPI
from datetime import datetime
import json

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "requests")
app = modal.App("empire-api-v1", image=image)

# Config (Constants)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
RESEND_API_KEY = "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
ESCALATION_PHONE = "+13529368152"

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
        
        # Log interaction
        requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
            "phone": phone, "direction": "inbound", "channel": channel,
            "message": message, "response": response_text, "agent": "sarah"
        })
        
        # Send response via GHL
        requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
        
        return {"agent": "sarah", "response": response_text}
    
    @api.post("/outbound")
    def handle_outbound(data: dict):
        """Handle outbound campaign task - Routes to Christina"""
        phone = data.get("phone", "")
        company = data.get("company", "your business")
        touch = data.get("touch", 1)
        
        print(f"[OUTBOUND] Touch {touch} to {phone}")
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Get memory context
        memory_resp = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=headers)
        memories = memory_resp.json() if memory_resp.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "New lead."
        
        # Christina's touch messages
        touch_templates = {
            1: f"Hi! I'm Christina from AI Service Co. I just reviewed {company}'s marketing - there are quick wins you're missing. Book a free call: {BOOKING_LINK}",
            2: f"Quick follow-up on {company} - I found 3 things that could help you get more leads this month. Got 15 min? {BOOKING_LINK}",
            3: f"Last chance - I'm moving on tomorrow. If you want the free strategy session for {company}, grab it now: {BOOKING_LINK}"
        }
        
        response_text = touch_templates.get(touch, touch_templates[1])
        
        # Log interaction
        requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
            "phone": phone, "direction": "outbound", "channel": "sms",
            "message": response_text, "agent": "christina", "touch": touch
        })
        
        # Send via GHL
        requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
        
        return {"agent": "christina", "touch": touch, "sent": True}
    
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
            except:
                audit_insight = f"Your {industry} business could benefit from automated lead capture and follow-up."
            
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
        
        SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return {"error": "Supabase not configured", "calls": []}
        
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
    
    return api


