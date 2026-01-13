"""
MODAL INBOUND FORWARDER
=======================
Handles Vapi webhooks for inbound calls and failover routing.
Runs on Modal cloud for 24/7 availability.
"""
import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")
app = modal.App("empire-inbound")
VAULT = modal.Secret.from_name("empire-vault")

# Backup phone for missed calls
BACKUP_PHONE = "+13529368152"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def vapi_webhook(payload: dict):
    """
    Handle ALL Vapi webhooks - call status, assistant request, etc.
    This is the main endpoint that Vapi should point to.
    """
    import requests
    import json
    from datetime import datetime
    
    msg_type = payload.get('message', {}).get('type') or payload.get('type', 'unknown')
    
    print(f"[VAPI WEBHOOK] Type: {msg_type}")
    print(f"[VAPI WEBHOOK] Payload: {json.dumps(payload)[:500]}")
    
    # Handle assistant-request (inbound call needs assistant)
    if msg_type == 'assistant-request':
        # Return Sarah as the assistant for inbound calls
        return {
            "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah
        }
    
    # Handle end-of-call-report
    if msg_type == 'end-of-call-report':
        call = payload.get('message', {}).get('call', {})
        ended_reason = payload.get('message', {}).get('endedReason', '')
        customer = call.get('customer', {}).get('number', 'unknown')
        
        print(f"[CALL ENDED] Customer: {customer}, Reason: {ended_reason}")
        
        # If call failed/no-answer, notify backup
        if ended_reason in ['no-answer', 'voicemail', 'machine-detected', 'busy', 'failed']:
            notify_backup(customer, ended_reason)
        
        return {"status": "logged", "reason": ended_reason}
    
    # Handle status-update
    if msg_type == 'status-update':
        status = payload.get('message', {}).get('status', '')
        print(f"[STATUS] {status}")
        return {"status": "received"}
    
    # Handle function-call (if assistant needs to call external functions)
    if msg_type == 'function-call':
        func_name = payload.get('message', {}).get('functionCall', {}).get('name', '')
        print(f"[FUNCTION CALL] {func_name}")
        return {"result": f"Function {func_name} executed"}
    
    return {"status": "received", "type": msg_type}


def notify_backup(caller_phone: str, reason: str):
    """Send SMS to backup number about missed call"""
    import requests
    
    message = f"MISSED CALL: {caller_phone} - Reason: {reason}. Call them back ASAP!"
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": BACKUP_PHONE,
            "message": message
        }, timeout=10)
        print(f"[SMS] Backup notified: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to notify backup: {e}")


@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "empire-inbound",
        "time": datetime.utcnow().isoformat(),
        "capabilities": ["vapi_webhook", "failover_sms", "assistant_routing"]
    }


@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def trigger_call(payload: dict):
    """Trigger an outbound call via Vapi"""
    import requests
    import os
    
    customer_phone = payload.get("phone")
    customer_name = payload.get("name", "there")
    
    if not customer_phone:
        return {"error": "Missing phone number"}
    
    VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
    SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"  # AI Service Co phone
    
    try:
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": PHONE_ID,
                "assistantId": SARAH_ID,
                "customer": {"number": customer_phone, "name": customer_name}
            },
            timeout=30
        )
        
        if resp.ok:
            return {"status": "call_initiated", "data": resp.json()}
        else:
            return {"status": "error", "code": resp.status_code, "message": resp.text[:200]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("Deploy: modal deploy modal_inbound.py")
