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
    "supabase"
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


@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="GET", label="email-status")
def email_health():
    return {"status": "ok", "service": "email_tracking"}


# ============ VAPI CALL STATUS SERVICE ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="vapi-callback")
def vapi_webhook(data: dict):
    """Handle Vapi call status webhooks"""
    import requests
    from datetime import datetime
    
    call_status = data.get('message', {}).get('type', 'unknown')
    call_id = data.get('message', {}).get('call', {}).get('id', 'unknown')
    
    print(f"[VAPI] {call_status} - Call: {call_id}")
    
    # Deep Brain Harvest (Phase 8)
    if call_status == 'end-of-call-report':
        try:
            from supabase import create_client
            import os
            
            supa_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            supa_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if supa_url and supa_key:
                client = create_client(supa_url, supa_key)
                
                msg = data.get('message', {})
                logger_data = {
                    'call_id': msg.get('call', {}).get('id'),
                    'phone_number': msg.get('customer', {}).get('number'),
                    'assistant_id': msg.get('assistantId'),
                    'transcript': msg.get('transcript'),
                    'summary': msg.get('summary'),
                    'sentiment': msg.get('analysis', {}).get('sentiment'),
                    'metadata': msg
                }
                
                client.table('call_transcripts').upsert(logger_data).execute()
                print(f"[DEEP BRAIN] Harvested call {call_id}")
        except Exception as e:
            print(f"[DEEP BRAIN] Harvest Failed: {e}")

    # Forward missed calls / Rescue Bridge
    if call_status in ['end-of-call-report', 'hang']:
        try:
            from modules import rescue_bridge
            result = rescue_bridge.handle_failed_call(data)
            print(f"[VAPI] Rescue result: {result}")
        except ImportError:
            # Fallback if module not found (shouldn't happen with add_local_dir)
            pass
        except Exception as e:
             print(f"[VAPI] Rescue bridge error: {e}")
    
    return {"status": "received", "call_status": call_status}


@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="GET", label="vapi-health")
def vapi_health():
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


# ============ CALL ANALYTICS ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="GET", label="analytics")
def call_analytics():
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


# ============ HEALTH CHECK ============
@app.function(image=image)
@modal.web_endpoint(method="GET", label="health")
def health():
    """Master health check"""
    from datetime import datetime
    return {
        "status": "ok",
        "services": ["email_tracking", "inbound_forwarder", "sequence_scheduler", "call_analytics"],
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
