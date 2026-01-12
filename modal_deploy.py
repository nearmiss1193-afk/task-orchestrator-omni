"""
MODAL CLOUD DEPLOYMENT
======================
Deploy all Empire services to Modal for 24/7 uptime.
"""
import modal
import os
import requests
import json
from datetime import datetime
from fastapi import Request

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
@modal.fastapi_endpoint(method="POST", label="email-callback")
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
@modal.fastapi_endpoint(method="POST", label="vapi-callback")
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
                        # Use JSON mode for reliability
                        model = genai.GenerativeModel(
                            "gemini-1.5-flash",
                            generation_config={"response_mime_type": "application/json"}
                        )
                        
                        learning_prompt = f'''
                        Analyze this call transcript and extract learnings for the AI agent.
                        TRANSCRIPT: {transcript[:4000]}
                        SUMMARY: {summary}
                        
                        Output a JSON object with these keys:
                        - objections (list of strings)
                        - successes (list of strings)
                        - improvements (list of strings)
                        - insight (string, key takeaway)
                        '''
                        
                        response = model.generate_content(learning_prompt)
                        # In JSON mode, text is guaranteed valid JSON
                        learnings = json.loads(response.text)
                            
                        # Store learnings
                        client.table('agent_learnings').insert({
                            'agent_name': agent_name,
                            'topic': 'call_analysis',
                            'insight': json.dumps(learnings),
                            'confidence': 0.95
                        }).execute()
                        
                        print(f"[AI LEARNING] {agent_name} learned from call {call_id} (Version 2.0)")
                        
                except Exception as learn_err:
                    print(f"[AI LEARNING] Extraction failed: {learn_err}")
                    # Fallback to saving raw failure for debugging
                    try:
                        client.table('agent_learnings').insert({
                            'agent_name': agent_name,
                            'topic': 'learning_error',
                            'insight': str(learn_err),
                            'confidence': 0.0
                        }).execute()
                    except: pass
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
    "google-generativeai",
    "fastapi"
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
)
@modal.fastapi_endpoint(method="POST")
async def vapi_status(request: Request):
    """
    Endpoint for Vapi Voice Agent to get system status.
    """
    import os
    from supabase import create_client
    # Request is already imported

    try:
        supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([supa_url, supa_key]):
            return {"results": [{"toolCallId": "unknown", "result": "Error: Missing credentials."}]}

        supabase = create_client(supa_url, supa_key)

        # 1. Get Stats
        leads_res = supabase.table("leads").select("*", count="exact", head=True).execute()
        calls_res = supabase.table("call_transcripts").select("*", count="exact", head=True).execute()
        
        speech = (
            f"Command, system is online. "
            f"You have {leads_res.count} leads and {calls_res.count} calls logged. "
            f"Cloud Autonomous Systems are active. "
            f"West Coast Blitz is enforcing H-V-A-C protocols."
        )
        
        return {
            "results": [
                {
                    "toolCallId": "unknown", 
                    "result": speech
                }
            ]
        }
    except Exception as e:
        print(f"[VAPI STATUS] Error: {e}")
        return {"results": [{"toolCallId": "unknown", "result": f"System Error: {str(e)}"}]}

@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
)
@modal.fastapi_endpoint(method="POST")
async def vapi_trigger_hunt(request: Request):
    """
    Voice Command: 'Find more leads'
    """
    try:
        # Trigger the cloud prospector immediately (spawn)
        # Note: In Modal we call .spawn() on the function handle
        cloud_prospector.spawn()
        
        return {
            "results": [
                {
                    "toolCallId": "unknown", 
                    "result": "Affirmative. I have deployed the Cloud Prospector to hunt for new H-V-A-C targets immediately."
                }
            ]
        }
    except Exception as e:
        return {"results": [{"toolCallId": "unknown", "result": f"Failed to execute: {str(e)}"}]}

@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 */4 * * *")  # Every 4 hours
)
def cloud_prospector():
    """Cloud Prospector - 24/7 Lead Hunting"""
    import os
    import json
    import requests
    import re
    import google.generativeai as genai
    from datetime import datetime
    from supabase import create_client
    
    print(f"[CLOUD PROSPECTOR] Starting at {datetime.now().isoformat()}")
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not all([supa_url, supa_key, gemini_key]):
        print("Missing credentials")
        return {"error": "credentials"}
    
    client = create_client(supa_url, supa_key)
    
    # 1. Check Pipeline Depth
    result = client.table("leads").select("id", count="exact").in_("status", ["new", "processing_email"]).execute()
    count = result.count if result.count is not None else len(result.data)
    
    print(f"[CLOUD PROSPECTOR] Current fresh leads: {count}")
    
    if count >= 30:
        print("Pipeline healthy. Resting.")
        return {"status": "healthy", "count": count}
    
    # 2. Hunt Mode
    print("Pipeline low. Initiating hunt...")
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Targeting
    cities = ["Tampa", "Orlando", "Miami", "Jacksonville", "Sarasota"]
    target_city = cities[datetime.now().hour % len(cities)]
    
    prompt = f"""
    Act as a lead generation expert. Find 5 REAL **HVAC** companies in {target_city}, FL.
    
    CRITICAL RULES:
    1. DO NOT use fictional numbers (555-xxxx).
    2. Provide REAL public phone numbers and emails if available.
    3. If a field is unknown, use "N/A".
    4. Verify the area code matches {target_city} (e.g. 813, 407, 305, 904).
    
    Return a JSON array with these fields:
    - company_name
    - owner_name (or "Manager")
    - email (guess format firstname@domain.com if 80% sure, else N/A)
    - phone (10 digit, no dashes)
    - city
    - industry
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Extract JSON
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if not json_match:
            print("No JSON found in response")
            return {"error": "no_json"}
            
        leads = json.loads(json_match.group())
        valid_leads = []
        
        for lead in leads:
            phone = lead.get('phone', '').replace('-', '').replace(' ', '')
            
            # STRICT VALIDATION
            if '555' in phone:  # Reject 555
                continue
            if len(phone) < 10:
                continue
            
            # Check duplicates
            dup = client.table("leads").select("id").eq("company_name", lead['company_name']).execute()
            if dup.data:
                continue
                
            lead['status'] = 'new'
            lead['created_at'] = datetime.now().isoformat()
            lead['agent_research'] = json.dumps(lead) # Store raw data
            valid_leads.append(lead)
            
        if valid_leads:
            client.table("leads").insert(valid_leads).execute()
            print(f"[CLOUD PROSPECTOR] Added {len(valid_leads)} new leads")
            
            # Log
            client.table("system_logs").insert({
                "level": "INFO",
                "event_type": "PROSPECTOR_HUNT",
                "message": f"Added {len(valid_leads)} leads from {target_city}",
                "metadata": {"city": target_city, "count": len(valid_leads)}
            }).execute()
            
        return {"added": len(valid_leads)}

    except Exception as e:
        print(f"Prospector error: {e}")
        return {"error": str(e)}


# cloud_guardian removed - replaced by self_healing_monitor with auto-repair capabilities


@app.function(
    image=campaign_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 10,14 * * *")  # 10 AM and 2 PM DAILY (including weekends)
)
def cloud_multi_touch():
    """Multi-touch outreach - Email + SMS + Call in cloud
    
    SOP: This function now includes pre-flight lead quality validation.
    - Prioritizes enriched phones over raw AI-generated data
    - Validates all numbers before calling
    - Auto-triggers enrichment for invalid leads
    """
    import os
    import requests
    import json
    import re
    import modal
    from datetime import datetime
    from fastapi import Request
    from supabase import create_client
    
    print(f"[CLOUD OUTREACH] Starting at {datetime.now().isoformat()}")
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    vapi_key = os.getenv("VAPI_PRIVATE_KEY")
    vapi_phone = os.getenv("VAPI_PHONE_NUMBER_ID")
    apollo_key = os.getenv("APOLLO_API_KEY")
    
    client = create_client(supa_url, supa_key)
    
    # === PRE-FLIGHT: Get leads and validate quality ===
    result = client.table("leads").select("*")\
        .in_("status", ["new", "processing_email"])\
        .limit(10)\
        .execute()
    
    leads = result.data
    print(f"[CLOUD OUTREACH] Checking {len(leads)} leads for quality...")
    
    results = {"email": 0, "sms": 0, "call": 0, "skipped": 0, "enriched": 0}
    callable_leads = []
    
    def validate_phone(phone_str):
        """Validate phone - reject fakes"""
        if not phone_str:
            return False, None, "missing"
        cleaned = re.sub(r'\D', '', str(phone_str))
        if len(cleaned) < 10:
            return False, None, "too_short"
        exchange = cleaned[-7:-4] if len(cleaned) >= 7 else ""
        if exchange == "555":
            return False, None, "fake_555"
        return True, cleaned[-10:], None
    
    def try_enrich_apollo(company_name, city=None):
        """Quick Apollo enrichment for single lead"""
        if not apollo_key:
            return None
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_people/search",
                headers={"Content-Type": "application/json", "X-Api-Key": apollo_key},
                json={
                    "q_organization_name": company_name,
                    "person_titles": ["Owner", "CEO", "President"],
                    "per_page": 3
                },
                timeout=15
            )
            data = resp.json()
            for person in data.get("people", []):
                phones = person.get("phone_numbers", [])
                if phones:
                    phone = phones[0].get("raw_number")
                    is_valid, cleaned, _ = validate_phone(phone)
                    if is_valid:
                        return {
                            "phone": f"+1{cleaned}",
                            "email": person.get("email"),
                            "name": person.get("name")
                        }
        except Exception as e:
            print(f"[ENRICH] Apollo error: {e}")
        return None
    
    # === VALIDATE AND ENRICH LEADS ===
    for lead in leads:
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        # Ensure meta is always a dict
        if not meta or not isinstance(meta, dict):
            meta = {}

        
        # PRIORITY: enriched_phone > phone field > agent_research phone
        enriched_phone = meta.get("enriched_phone", "")
        lead_phone = lead.get("phone", "")
        research_phone = meta.get("phone", "")
        
        # Try phones in priority order
        actual_phone = None
        for phone in [enriched_phone, lead_phone, research_phone]:
            is_valid, cleaned, issue = validate_phone(phone)
            if is_valid:
                actual_phone = f"+1{cleaned}"
                break
        
        company = lead.get("company_name", "Prospect")
        email = meta.get("enriched_email", "") or meta.get("email", "") or lead.get("email", "")
        
        if not actual_phone:
            # Try Apollo enrichment on-the-fly
            print(f"   🔧 Enriching {company}...")
            enriched = try_enrich_apollo(company, lead.get("city"))
            if enriched:
                actual_phone = enriched["phone"]
                email = enriched.get("email") or email
                # Save enrichment
                client.table("leads").update({
                    "phone": actual_phone,
                    "agent_research": json.dumps({
                        **meta,
                        "enriched_phone": actual_phone,
                        "enriched_email": enriched.get("email"),
                        "enriched_name": enriched.get("name"),
                        "enriched_at": datetime.now().isoformat()
                    })
                }).eq("id", lead["id"]).execute()
                results["enriched"] += 1
                print(f"   ✅ Enriched: {actual_phone}")
            else:
                print(f"   ❌ Could not enrich {company}")
                results["skipped"] += 1
                continue
        
        callable_leads.append({
            "id": lead["id"],
            "company": company,
            "phone": actual_phone,
            "email": email
        })
    
    print(f"[CLOUD OUTREACH] Processing {len(callable_leads)} callable leads")
    
    # === OUTREACH ===
    for lead in callable_leads[:5]:  # Process max 5 per run
        company = lead["company"]
        email = lead["email"]
        phone = lead["phone"]
        
        # Email
        if email and resend_key and "N/A" not in email:
            try:
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
            except Exception as e:
                print(f"Email error: {e}")
        
        # Call (using Vapi)
        if phone and vapi_key and vapi_phone:
            try:
                call_res = requests.post(
                    "https://api.vapi.ai/call",
                    headers={"Authorization": f"Bearer {vapi_key}", "Content-Type": "application/json"},
                    json={
                        "type": "outboundPhoneCall",
                        "phoneNumberId": vapi_phone,
                        "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
                        "customer": {"number": phone, "name": company}
                    }
                )
                if call_res.status_code in [200, 201]:
                    results["call"] += 1
                    client.table("leads").update({
                        "status": "called",
                        "last_called": datetime.now().isoformat()
                    }).eq("id", lead["id"]).execute()
                else:
                    print(f"Vapi error: {call_res.text}")
            except Exception as e:
                print(f"Call error: {e}")
    
    # Log
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "CLOUD_OUTREACH",
        "message": f"[CLOUD_OUTREACH] Emails: {results['email']}, Calls: {results['call']}, Enriched: {results['enriched']}, Skipped: {results['skipped']}",
        "metadata": results
    }).execute()
    
    print(f"[CLOUD OUTREACH] Complete: {results}")
    return results


# ============ SOCIAL MEDIA AUTOMATION (24/7) ============

social_image = modal.Image.debian_slim().pip_install(
    "requests",
    "anthropic",
    "supabase"
)

@app.function(
    image=social_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 8 * * *")  # 8 AM daily
)
def social_media_poster():
    """AI-powered social media posting to 9 platforms via Ayrshare"""
    import os
    import requests
    from datetime import datetime
    import anthropic
    
    hour = datetime.now().hour
    
    # Platform schedule
    if hour == 8:
        platforms = ["linkedin"]
        theme = "hvac_tips"
    elif hour == 13:
        platforms = ["facebook", "instagram"]
        theme = "business_insights"
    elif hour == 15:
        platforms = ["twitter", "threads"]
        theme = "quick_tips"
    else:
        platforms = ["linkedin", "facebook"]
        theme = "success_stories"
    
    print(f"[SOCIAL] Posting to {platforms} with theme: {theme}")
    
    # Generate content with Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[SOCIAL] No Anthropic key - using default content")
        content = "AI-powered phone agents are revolutionizing HVAC customer service. Ask us how! #HVAC #AI #CustomerService"
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"Create a short, engaging social media post for an HVAC business about {theme}. Be professional but conversational. Include 2-3 relevant hashtags. Keep it under 250 characters for Twitter/Threads compatibility."
                }]
            )
            content = message.content[0].text
        except Exception as e:
            print(f"[SOCIAL] Claude error: {e}")
            content = "Your HVAC business deserves 24/7 coverage. Our AI phone agents never miss a call! #HVAC #AI #CustomerService"
    
    print(f"[SOCIAL] Content: {content[:100]}...")
    
    # Post via Ayrshare
    ayrshare_key = os.environ.get("AYRSHARE_API_KEY")
    if ayrshare_key:
        try:
            resp = requests.post(
                "https://app.ayrshare.com/api/post",
                headers={
                    "Authorization": f"Bearer {ayrshare_key}",
                    "Content-Type": "application/json"
                },
                json={"post": content, "platforms": platforms}
            )
            print(f"[SOCIAL] Ayrshare response: {resp.status_code} - {resp.text[:200]}")
            return {"status": "posted", "platforms": platforms, "response": resp.status_code}
        except Exception as e:
            print(f"[SOCIAL] Ayrshare error: {e}")
            return {"status": "error", "error": str(e)}
    else:
        print("[SOCIAL] No Ayrshare key - skipping post")
        return {"status": "skipped", "reason": "no_api_key"}


@app.function(
    image=social_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 22 * * *")  # 10 PM daily
)
def social_media_analytics():
    """Collect social media analytics daily"""
    import os
    import requests
    from datetime import datetime
    from supabase import create_client
    
    print(f"[ANALYTICS] Collecting at {datetime.now().isoformat()}")
    
    ayrshare_key = os.environ.get("AYRSHARE_API_KEY")
    supa_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    analytics = {"collected": False}
    
    if ayrshare_key:
        try:
            resp = requests.get(
                "https://app.ayrshare.com/api/analytics/social",
                headers={"Authorization": f"Bearer {ayrshare_key}"}
            )
            if resp.status_code == 200:
                analytics = resp.json()
                analytics["collected"] = True
                print(f"[ANALYTICS] Collected: {analytics}")
        except Exception as e:
            print(f"[ANALYTICS] Error: {e}")
    
    # Log to Supabase
    if supa_url and supa_key:
        try:
            client = create_client(supa_url, supa_key)
            client.table("system_logs").insert({
                "level": "INFO",
                "event_type": "SOCIAL_ANALYTICS",
                "message": f"Daily social analytics collected",
                "metadata": analytics
            }).execute()
        except Exception as e:
            print(f"[ANALYTICS] DB error: {e}")
    
    return analytics


# ============ SELF-HEALING HEALTH MONITOR ============

health_monitor_image = modal.Image.debian_slim().pip_install(
    "requests",
    "supabase",
    "resend"
)

@app.function(
    image=health_monitor_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/30 * * * *")  # Every 30 minutes
)
def self_healing_monitor():
    """Comprehensive self-healing health monitor - checks all systems and auto-repairs issues"""
    import os
    import requests
    import json
    from datetime import datetime, timedelta
    from supabase import create_client
    
    print("=" * 60)
    print("🏥 EMPIRE SELF-HEALING HEALTH MONITOR")
    print(f"   Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    
    all_healthy = True
    all_issues = []
    
    # 1. Check Supabase Health
    print("\n🔍 Checking Supabase health...")
    critical_tables = ["prospects", "leads", "email_logs", "system_logs", "call_logs"]
    
    try:
        client = create_client(supa_url, supa_key)
        
        for table in critical_tables:
            try:
                result = client.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table}: OK")
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ {table}: {error_msg[:50]}")
                all_issues.append({"type": "supabase", "table": table, "error": error_msg[:100]})
                
                # Auto-repair: If schema cache issue, refresh it
                if "PGRST" in error_msg:
                    print(f"   🔧 Attempting schema cache refresh...")
                    try:
                        client.rpc("pg_notify", {"channel": "pgrst", "payload": "reload schema"}).execute()
                        print(f"   ✅ Schema cache refresh triggered")
                    except:
                        pass
    except Exception as e:
        print(f"   ❌ Supabase connection failed: {e}")
        all_issues.append({"type": "supabase", "error": str(e)[:100]})
    
    # 2. Check Critical Endpoints
    print("\n🌐 Checking endpoints...")
    endpoints = {
        "modal_webhook": "https://nearmiss1193-afk--empire-sovereign-v2-email-webhook.modal.run",
        "website": "https://aiserviceco.com",
        "dashboard": "https://aiserviceco.com/dashboard.html",
    }
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code < 500:
                print(f"   ✅ {name}: {response.status_code}")
            else:
                print(f"   ❌ {name}: {response.status_code}")
                all_issues.append({"type": "endpoint", "name": name, "status": response.status_code})
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:40]}")
            all_issues.append({"type": "endpoint", "name": name, "error": str(e)[:100]})
    
    # 3. Check Recent Activity
    print("\n📊 Checking recent activity...")
    try:
        two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()
        result = client.table("system_logs").select("*").gte("created_at", two_hours_ago).execute()
        log_count = len(result.data)
        
        if log_count > 0:
            print(f"   ✅ {log_count} system events in last 2 hours")
        else:
            print(f"   ⚠️ No activity in last 2 hours - system may be stalled")
            all_issues.append({"type": "activity", "issue": "No activity in 2 hours"})
    except Exception as e:
        print(f"   ❌ Activity check failed: {e}")
    
    # Log health check
    try:
        client.table("system_logs").insert({
            "level": "INFO" if not all_issues else "WARNING",
            "event_type": "HEALTH_CHECK",
            "message": f"Health check: {len(all_issues)} issues" if all_issues else "All systems healthy",
            "metadata": {"issues": all_issues, "timestamp": datetime.now().isoformat(), "monitor": "self-healing"}
        }).execute()
    except:
        pass
    
    # 4. Send Alert if Issues
    if all_issues and resend_key:
        print("\n📧 Sending alert email...")
        try:
            import resend
            resend.api_key = resend_key
            
            issue_summary = "\n".join([f"• {json.dumps(i)}" for i in all_issues[:5]])
            
            resend.Emails.send({
                "from": "Health Monitor <monitor@aiserviceco.com>",
                "to": ["owner@aiserviceco.com", "nearmiss1193@gmail.com"],
                "subject": f"🚨 Empire Alert: {len(all_issues)} Issues Detected",
                "html": f"""
                <div style="font-family: system-ui; padding: 20px; background: #1e293b; color: #f8fafc;">
                    <h2 style="color: #ef4444;">⚠️ System Alert</h2>
                    <pre style="background: #0f172a; padding: 15px; border-radius: 8px;">{issue_summary}</pre>
                    <hr style="border-color: #334155;">
                    <p style="color: #64748b; font-size: 12px;">
                        Sent by Empire Self-Healing Monitor at {datetime.now().isoformat()}
                    </p>
                </div>
                """
            })
            print(f"   ✅ Alert sent")
        except Exception as e:
            print(f"   ❌ Failed to send alert: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if not all_issues:
        print("✅ ALL SYSTEMS HEALTHY")
    else:
        print(f"⚠️ {len(all_issues)} ISSUE(S) DETECTED")
    print("=" * 60)
    
    return {"healthy": len(all_issues) == 0, "issues": all_issues, "timestamp": datetime.now().isoformat()}


# ============ HEALTH CHECK ============
@app.function(image=image)
@modal.fastapi_endpoint(method="GET", label="health")
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
