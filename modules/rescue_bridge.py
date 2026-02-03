import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def handle_failed_call(call_data: dict):
    """
    Analyzes a failed Vapi call and triggers a rescue action (SMS/Email to Owner).
    """
    call_id = call_data.get('message', {}).get('call', {}).get('id', 'unknown')
    ended_reason = call_data.get('message', {}).get('endedReason', 'unknown')
    customer_phone = call_data.get('message', {}).get('call', {}).get('customer', {}).get('number')
    
    print(f"[RESCUE] Analyzing failure for {call_id} (Reason: {ended_reason})")
    
    if ended_reason in ['no-answer', 'busy', 'voicemail']:
        # Standard sales failure, maybe schedule retry?
        return {"status": "retry_scheduled", "reason": ended_reason}
        
    if ended_reason in ['pipeline-error', 'assistant-error', 'silence-timed-out', 'failed']:
        # System failure -> IMMEDIATE RESCUE
        return trigger_rescue_alert(customer_phone, ended_reason)
        
    return {"status": "analyzed", "action": "none"}

def trigger_rescue_alert(customer_phone, reason):
    """
    Alerts the owner to call the customer back immediately.
    """
    owner_phone = os.getenv("TEST_PHONE") or os.getenv("OWNER_PHONE")
    webhook_url = os.getenv("GHL_SMS_WEBHOOK_URL") or os.getenv("GHL_SMS_WEBHOOK")
    
    if not owner_phone or not webhook_url:
        print("[RESCUE] Missing config (TEST_PHONE or GHL_SMS_WEBHOOK). Cannot alert.")
        return {"status": "failed", "error": "missing_config"}
        
    message = f"🚨 MISSED LEAD ALERT 🚨\nReason: {reason}\nCustomer: {customer_phone}\n\nCall them back ASAP!"
    
    try:
        requests.post(webhook_url, json={
            "phone": owner_phone,
            "message": message
        })
        print(f"[RESCUE] Alert sent to {owner_phone}")
        return {"status": "alert_sent", "recipient": owner_phone}
    except Exception as e:
        print(f"[RESCUE] Failed to send alert: {e}")
        return {"status": "failed", "error": str(e)}
