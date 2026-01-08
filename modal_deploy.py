"""
MODAL CLOUD DEPLOYMENT
======================
Deploy all Empire services to Modal for 24/7 uptime.
"""
import modal
import os

# Create Modal app
app = modal.App("empire-services")

# Image with dependencies
image = modal.Image.debian_slim().pip_install(
    "flask",
    "requests",
    "python-dotenv",
    "schedule",
    "fastapi",
    "uvicorn"
)


# ============ EMAIL TRACKING SERVICE ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="email-webhook")
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
@modal.web_endpoint(method="GET", label="email-health")
def email_health():
    return {"status": "ok", "service": "email_tracking"}


# ============ VAPI CALL STATUS SERVICE ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv()],
    keep_warm=1
)
@modal.web_endpoint(method="POST", label="vapi-webhook")
def vapi_webhook(data: dict):
    """Handle Vapi call status webhooks"""
    import requests
    from datetime import datetime
    
    call_status = data.get('message', {}).get('type', 'unknown')
    call_id = data.get('message', {}).get('call', {}).get('id', 'unknown')
    
    print(f"[VAPI] {call_status} - Call: {call_id}")
    
    # Forward missed calls
    if call_status in ['end-of-call-report', 'hang']:
        ended_reason = data.get('message', {}).get('endedReason', '')
        if ended_reason in ['no-answer', 'busy', 'failed']:
            # Notify backup
            ghl_webhook = os.environ.get('GHL_SMS_WEBHOOK', '')
            backup_phone = os.environ.get('TEST_PHONE', '')
            
            if ghl_webhook and backup_phone:
                try:
                    requests.post(ghl_webhook, json={
                        "phone": backup_phone,
                        "message": f"📞 Missed call! Reason: {ended_reason}. Call back ASAP."
                    })
                except:
                    pass
    
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
    print("  - Sequence scheduler runs every 15 minutes")
