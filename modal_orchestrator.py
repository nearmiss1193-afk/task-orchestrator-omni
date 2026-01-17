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
    
    api = FastAPI(title="Sovereign Orchestrator", version="2.0")
    
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
    
    return api
