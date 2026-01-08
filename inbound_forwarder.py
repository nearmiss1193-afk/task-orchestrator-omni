"""
INBOUND CALL FORWARDING
=======================
Handles failed AI call pickups by forwarding to backup number.
Uses Vapi webhook to detect call failures.
"""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# Backup number to forward failed calls to
BACKUP_PHONE = os.getenv('TEST_PHONE', '+13529368152')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"


@app.route('/webhook/vapi/call-status', methods=['POST'])
def vapi_call_status():
    """
    Handle Vapi call status webhooks.
    Detects failed pickups and forwards to backup.
    """
    data = request.json
    
    call_type = data.get('type')
    call_status = data.get('status')
    customer_phone = data.get('customer', {}).get('number')
    
    print(f"[VAPI WEBHOOK] Type: {call_type}, Status: {call_status}")
    
    # Detect failed inbound calls
    if call_type == 'inbound' and call_status in ['failed', 'no-answer', 'busy']:
        print(f"[ALERT] Failed inbound from {customer_phone} - forwarding to backup")
        
        # Notify backup phone via SMS
        notify_backup(customer_phone, call_status)
        
        # Log missed call
        log_missed_call(customer_phone, call_status)
        
        return jsonify({"action": "forward", "status": "notified"})
    
    return jsonify({"status": "received"})


def notify_backup(caller_phone: str, reason: str):
    """Send SMS to backup number about missed call"""
    message = f"🚨 MISSED CALL: {caller_phone} - Reason: {reason}. Call them back ASAP!"
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": BACKUP_PHONE,
            "message": message
        })
        print(f"[SMS] Backup notified: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to notify backup: {e}")


def log_missed_call(phone: str, reason: str):
    """Log missed call to file"""
    import json
    from datetime import datetime
    
    log_file = "missed_calls.json"
    
    entry = {
        "phone": phone,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(entry)
    
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"[LOG] Missed call logged: {entry}")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "inbound-forwarder"})


if __name__ == "__main__":
    print("Starting Inbound Call Forwarder...")
    print(f"Backup phone: {BACKUP_PHONE}")
    app.run(host='0.0.0.0', port=5050, debug=True)
