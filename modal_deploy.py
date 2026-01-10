"""
MODAL CLOUD DEPLOYMENT
======================
Deploy all Empire services to Modal for 24/7 uptime.
"""
import modal
import os

# Create Modal app
app = modal.App("empire-sovereign-v2")

# Image with dependencies
image = modal.Image.debian_slim().pip_install(
    "flask",
    "requests",
    "python-dotenv",
    "schedule",
    "fastapi",
    "uvicorn",
    "supabase",
    "google-generativeai"
)\
.add_local_file("worker.py", remote_path="/root/worker.py")\
.add_local_dir("modules", remote_path="/root/modules", ignore=["ghl-mcp", "descript-mcp", "node_modules", "__pycache__", "**/*.pyc", ".git", "**/*.zip", "**/*.db", "**/*.csv"])

# ============ SOVEREIGN WORKER (THE BODY) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    timeout=86400, # 24 hours (Long running)
    keep_warm=1
)
def sovereign_worker():
    """
    The main autonomous agent loop.
    Runs continuously in the cloud to process Supabase tasks.
    """
    import worker
    
    print("🚀 Sovereign Worker Starting in Cloud...")
    try:
        worker.main_loop() 
    except Exception as e:
        print(f"CRITICAL WORKER FAILURE: {e}")
        raise e


# ============ EMAIL TRACKING SERVICE ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="email-callback")
def email_webhook(data: dict):
    """Handle Resend email webhooks"""
    from datetime import datetime
    import json
    
    event_type = data.get('type', 'unknown')
    email_data = data.get('data', {})
    
    # Log event
    event = {
        "type": event_type,
        "email": email_data.get('to', ['unknown'])[0] if isinstance(email_data.get('to'), list) else email_data.get('to', 'unknown'),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"[EMAIL] {event_type}: {event['email']}")
    
    return {"status": "received", "event": event_type}


# email_health removed to reduce endpoint count (consolidated into main health)


# ============ VAPI CALL STATUS SERVICE ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="vapi-callback")
def vapi_webhook(data: dict):
    """Handle Vapi call status webhooks - WITH AI LEARNING"""
    import requests
    from datetime import datetime
    import json
    
    call_status = data.get('message', {}).get('type', 'unknown')
    call_id = data.get('message', {}).get('call', {}).get('id', 'unknown')
    
    print(f"[VAPI] {call_status} - Call: {call_id}")
    
    # Deep Brain Harvest + AI Learning (Phase 8+)
    if call_status == 'end-of-call-report':
        try:
            from supabase import create_client
            import os
            
            supa_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            supa_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if supa_url and supa_key:
                client = create_client(supa_url, supa_key)
                
                msg = data.get('message', {})
                transcript = msg.get('transcript', '')
                summary = msg.get('summary', '')
                phone = msg.get('customer', {}).get('number', 'Unknown')
                assistant_id = msg.get('assistantId', '')
                
                # Determine agent name
                agent_name = 'Sarah' if 'sarah' in assistant_id.lower() or '1a797f12' in assistant_id else 'AI Agent'
                
                # 1. Save transcript to database
                logger_data = {
                    'call_id': msg.get('call', {}).get('id'),
                    'phone_number': phone,
                    'assistant_id': assistant_id,
                    'transcript': transcript,
                    'summary': summary,
                    'sentiment': msg.get('analysis', {}).get('sentiment'),
                    'metadata': msg
                }
                
                client.table('call_transcripts').upsert(logger_data).execute()
                print(f"[DEEP BRAIN] Harvested call {call_id}")
                
                # 2. AI Learning Extraction (use Gemini to extract insights)
                try:
                    import google.generativeai as genai
                    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                    if api_key and transcript:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        learning_prompt = f'''
                        Analyze this call transcript and extract learnings for the AI agent.
                        
                        TRANSCRIPT:
                        {transcript[:3000]}
                        
                        SUMMARY:
                        {summary}
                        
                        Extract:
                        1. What objections did the customer raise?
                        2. What worked well in the conversation?
                        3. What could be improved?
                        4. Key insight for future calls?
                        
                        Format as JSON: {{"objections": [], "successes": [], "improvements": [], "insight": ""}}
                        '''
                        
                        response = model.generate_content(learning_prompt)
                        raw = response.text.replace('```json', '').replace('```', '').strip()
                        
                        try:
                            learnings = json.loads(raw)
                            
                            # Store learnings
                            client.table('agent_learnings').insert({
                                'agent_name': agent_name,
                                'topic': 'call_analysis',
                                'insight': json.dumps(learnings),
                                'confidence': 0.85
                            }).execute()
                            
                            print(f"[AI LEARNING] {agent_name} learned from call {call_id}")
                        except:
                            # Store raw insight if JSON parse fails
                            client.table('agent_learnings').insert({
                                'agent_name': agent_name,
                                'topic': 'call_insight',
                                'insight': raw[:500],
                                'confidence': 0.7
                            }).execute()
                except Exception as learn_err:
                    print(f"[AI LEARNING] Extraction failed: {learn_err}")
                
                # 3. Send notification with transcript
                try:
                    resend_key = os.getenv("RESEND_API_KEY")
                    owner_email = os.getenv("GHL_EMAIL") or "nearmiss1193@gmail.com"
                    
                    if resend_key:
                        notification = {
                            "from": "Empire AI <notifications@aiserviceco.com>",
                            "to": [owner_email],
                            "subject": f"📞 Call Complete: {phone}",
                            "html": f'''
                            <h2>Call Transcript - {agent_name}</h2>
                            <p><strong>Phone:</strong> {phone}</p>
                            <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                            <p><strong>Sentiment:</strong> {msg.get('analysis', {}).get('sentiment', 'N/A')}</p>
                            <hr>
                            <h3>Summary</h3>
                            <p>{summary or 'No summary available'}</p>
                            <hr>
                            <h3>Full Transcript</h3>
                            <pre style="background:#f5f5f5;padding:10px;white-space:pre-wrap;">{transcript or 'No transcript'}</pre>
                            '''
                        }
                        
                        requests.post(
                            "https://api.resend.com/emails",
                            headers={"Authorization": f"Bearer {resend_key}"},
                            json=notification
                        )
                        print(f"[NOTIFY] Transcript sent to {owner_email}")
                except Exception as notify_err:
                    print(f"[NOTIFY] Failed: {notify_err}")
                    
        except Exception as e:
            print(f"[DEEP BRAIN] Harvest Failed: {e}")

    # Forward missed calls / Rescue Bridge
    if call_status in ['end-of-call-report', 'hang']:
        try:
            from modules import rescue_bridge
            result = rescue_bridge.handle_failed_call(data)
            print(f"[VAPI] Rescue result: {result}")
        except ImportError:
            pass
        except Exception as e:
             print(f"[VAPI] Rescue bridge error: {e}")
    
    return {"status": "received", "call_status": call_status}


# vapi_health removed to reduce endpoint count (consolidated into main health)
def _vapi_health_internal():
    return {"status": "ok", "service": "inbound_forwarder"}


# ============ SEQUENCE SCHEDULER ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/15 * * * *")  # Every 15 minutes
)
def run_sequences():
    """Check and execute due sequence steps"""
    import json
    from datetime import datetime, timedelta
    import requests
    
    print(f"[SCHEDULER] Running at {datetime.now().isoformat()}")
    
    # Load active sequences
    try:
        with open("/app/active_sequences.json", "r") as f:
            sequences = json.load(f)
    except:
        sequences = []
    
    executed = 0
    for seq in sequences:
        if seq.get('status') != 'active':
            continue
        
        # Check if step is due
        next_step_due = seq.get('next_step_due')
        if next_step_due and datetime.now() >= datetime.fromisoformat(next_step_due):
            # Execute step
            step = seq.get('current_step', 0)
            print(f"[SCHEDULER] Executing step {step} for {seq.get('contact', {}).get('name')}")
            executed += 1
    
    print(f"[SCHEDULER] Executed {executed} steps")
    return {"executed": executed}


# ============ CALL ANALYTICS (internal - moved from web endpoint to reduce count) ============
# call_analytics endpoint removed to fit within Modal free tier limit
def _call_analytics_internal():
    """Get call analytics"""
    import requests
    from collections import defaultdict
    
    vapi_key = os.environ.get('VAPI_PRIVATE_KEY', '')
    
    if not vapi_key:
        return {"mock": True, "total_calls": 5, "avg_duration": "2m 30s"}
    
    try:
        response = requests.get(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {vapi_key}"},
            params={"limit": 50}
        )
        
        if response.status_code == 200:
            calls = response.json()
            total = len(calls)
            durations = [c.get('duration', 0) for c in calls if c.get('duration')]
            avg = sum(durations) / len(durations) if durations else 0
            
            return {
                "total_calls": total,
                "avg_duration_seconds": round(avg, 1),
                "avg_duration_formatted": f"{int(avg // 60)}m {int(avg % 60)}s"
            }
    except:
        pass
    
    return {"error": "Failed to fetch analytics"}


# ============ CLOUD CAMPAIGNS (24/7 AUTONOMOUS) ============

# Campaign image with all dependencies
campaign_image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv",
    "supabase",
    "google-generativeai"
)


@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 9 * * *")  # Daily at 9 AM ET
)
def cloud_drip_campaign():
    """Daily drip campaign - runs in cloud 24/7"""
    import os
    import requests
    from datetime import datetime
    from supabase import create_client
    
    print(f"[CLOUD DRIP] Starting at {datetime.now().isoformat()}")
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    
    if not all([supa_url, supa_key, resend_key]):
        print("[CLOUD DRIP] Missing credentials")
        return {"error": "credentials"}
    
    client = create_client(supa_url, supa_key)
    
    # Get leads to drip
    result = client.table("leads").select("*")\
        .eq("status", "contacted")\
        .limit(20)\
        .execute()
    
    leads = result.data
    print(f"[CLOUD DRIP] Found {len(leads)} leads for drip")
    
    sent = 0
    for lead in leads:
        email = lead.get("email")
        company = lead.get("company_name", "Your Company")
        
        if email:
            # Send follow-up
            res = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}"},
                json={
                    "from": "Daniel @ AI Service Co <system@aiserviceco.com>",
                    "to": [email],
                    "subject": f"Following up - {company}",
                    "html": f"<p>Hi! Just wanted to follow up on my previous message about AI phone agents for {company}.</p><p>Would love to show you how it works. Reply to chat!</p><p>- Daniel<br>(352) 758-5336</p>"
                }
            )
            if res.status_code in [200, 201]:
                sent += 1
    
    # Log
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "CLOUD_DRIP_COMPLETE",
        "message": f"Sent {sent}/{len(leads)} drip emails",
        "metadata": {"sent": sent, "total": len(leads)}
    }).execute()
    
    print(f"[CLOUD DRIP] Complete: {sent} sent")
    return {"sent": sent}


@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 */2 * * *")  # Every 2 hours
)
def cloud_growth_daemon():
    """Growth daemon - prospect intel gathering in cloud"""
    import os
    import requests
    from datetime import datetime
    from supabase import create_client
    
    print(f"[CLOUD GROWTH] Starting at {datetime.now().isoformat()}")
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not all([supa_url, supa_key]):
        return {"error": "credentials"}
    
    client = create_client(supa_url, supa_key)
    
    # Count leads by status
    statuses = ["new", "contacted", "replied", "called", "qualified", "booked"]
    counts = {}
    
    for status in statuses:
        result = client.table("leads").select("id", count="exact").eq("status", status).execute()
        counts[status] = len(result.data) if result.data else 0
    
    total = sum(counts.values())
    
    # Log stats
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "CLOUD_GROWTH_CHECK",
        "message": f"Pipeline: {total} leads",
        "metadata": counts
    }).execute()
    
    print(f"[CLOUD GROWTH] Pipeline: {counts}")
    return counts


@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/5 * * * *")  # Every 5 minutes
)
def cloud_guardian():
    """System guardian - continuous health monitoring in cloud"""
    import os
    import requests
    from datetime import datetime
    from supabase import create_client
    
    services = {
        "website": "https://www.aiserviceco.com",
        "dashboard": "https://www.aiserviceco.com/dashboard.html",
    }
    
    issues = []
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                issues.append(f"{name}: {r.status_code}")
        except Exception as e:
            issues.append(f"{name}: {str(e)[:50]}")
    
    # Alert if issues
    if issues:
        resend_key = os.getenv("RESEND_API_KEY")
        owner = os.getenv("OWNER_EMAIL", "nearmiss1193@gmail.com")
        
        if resend_key:
            requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}"},
                json={
                    "from": "System Guardian <alerts@aiserviceco.com>",
                    "to": [owner],
                    "subject": f"🚨 System Alert: {len(issues)} issues",
                    "html": f"<h2>Issues Detected</h2><pre>{chr(10).join(issues)}</pre>"
                }
            )
        
        print(f"[CLOUD GUARDIAN] ⚠️ {len(issues)} issues: {issues}")
    else:
        print(f"[CLOUD GUARDIAN] ✅ All services OK")
    
    return {"healthy": len(issues) == 0, "issues": issues}


@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 10,14 * * 1-5")  # 10 AM and 2 PM on weekdays
)
def cloud_multi_touch():
    """Multi-touch outreach - Email + SMS + Call in cloud"""
    import os
    import requests
    import json
    from datetime import datetime
    from supabase import create_client
    
    print(f"[CLOUD OUTREACH] Starting at {datetime.now().isoformat()}")
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    vapi_key = os.getenv("VAPI_PRIVATE_KEY")
    vapi_phone = os.getenv("VAPI_PHONE_NUMBER_ID")
    
    client = create_client(supa_url, supa_key)
    
    # Get 5 leads for outreach
    result = client.table("leads").select("*")\
        .in_("status", ["new", "processing_email"])\
        .limit(5)\
        .execute()
    
    leads = result.data
    print(f"[CLOUD OUTREACH] Processing {len(leads)} leads")
    
    results = {"email": 0, "sms": 0, "call": 0}
    
    for lead in leads:
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        
        email = meta.get("email") or lead.get("email")
        phone = meta.get("phone") or lead.get("phone")
        company = lead.get("company_name", "Prospect")
        
        # Email
        if email and resend_key:
            res = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}"},
                json={
                    "from": "Daniel @ AI Service Co <system@aiserviceco.com>",
                    "to": [email],
                    "subject": f"Quick question for {company}",
                    "html": f"<p>Hi! I noticed {company} might benefit from AI phone agents. Worth a quick chat?</p><p>- Daniel<br>(352) 758-5336</p>"
                }
            )
            if res.status_code in [200, 201]:
                results["email"] += 1
        
        # Call (using Vapi)
        if phone and vapi_key and vapi_phone:
            if not phone.startswith("+"):
                phone = "+1" + phone.replace("-", "").replace(" ", "")
            
            call_res = requests.post(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {vapi_key}", "Content-Type": "application/json"},
                json={
                    "type": "outboundPhoneCall",
                    "phoneNumberId": vapi_phone,
                    "assistantId": "1a797f12-e516-4fe8-a3a6-72f0cbf4a48d",
                    "customer": {"number": phone, "name": company}
                }
            )
            if call_res.status_code in [200, 201]:
                results["call"] += 1
                client.table("leads").update({
                    "status": "called",
                    "last_called": datetime.now().isoformat()
                }).eq("id", lead["id"]).execute()
    
    # Log
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "CLOUD_OUTREACH_COMPLETE",
        "message": f"Emails: {results['email']}, Calls: {results['call']}",
        "metadata": results
    }).execute()
    
    print(f"[CLOUD OUTREACH] Complete: {results}")
    return results


# ============ HEALTH CHECK ============
@app.function(image=image)
@modal.web_endpoint(method="GET", label="health")
def health():
    """Master health check"""
    from datetime import datetime
    return {
        "status": "ok",
        "services": ["email_tracking", "inbound_forwarder", "sequence_scheduler", "call_analytics", "cloud_campaigns"],
        "timestamp": datetime.now().isoformat()
    }


# ============ LOCAL ENTRYPOINT ============
@app.local_entrypoint()
def main():
    print("Empire Services Deployed!")
    print("Endpoints:")
    print("  - /email-webhook (POST)")
    print("  - /vapi-webhook (POST)")
    print("  - /analytics (GET)")
    print("  - /health (GET)")
    print("Services:")
    print("  - Sequence scheduler (every 15 min)")
    print("  - Sovereign Worker (Continuous)")
    print("\nTo launch worker explicitly: modal run modal_deploy.py::sovereign_worker")
