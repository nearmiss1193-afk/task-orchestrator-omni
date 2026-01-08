"""
EMAIL TRACKING WEBHOOK
======================
Tracks email opens, clicks, and bounces via Resend webhooks.
Stores tracking data to Supabase.
"""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Local tracking log
TRACKING_LOG = "email_tracking.json"


@app.route('/webhook/resend', methods=['POST'])
def resend_webhook():
    """
    Handle Resend email event webhooks.
    Events: delivered, opened, clicked, bounced, complained
    """
    data = request.json
    
    event_type = data.get('type')
    email_id = data.get('data', {}).get('email_id')
    recipient = data.get('data', {}).get('to', ['unknown'])[0]
    
    print(f"[RESEND] {event_type} - {recipient}")
    
    # Log event
    log_event({
        "event": event_type,
        "email_id": email_id,
        "recipient": recipient,
        "timestamp": datetime.now().isoformat(),
        "raw_data": data
    })
    
    # Handle specific events
    if event_type == 'email.opened':
        handle_open(email_id, recipient)
    elif event_type == 'email.clicked':
        link = data.get('data', {}).get('click', {}).get('link')
        handle_click(email_id, recipient, link)
    elif event_type == 'email.bounced':
        handle_bounce(email_id, recipient)
    
    return jsonify({"status": "received"})


def log_event(event: dict):
    """Log email event to file"""
    try:
        with open(TRACKING_LOG, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(event)
    
    with open(TRACKING_LOG, "w") as f:
        json.dump(logs, f, indent=2)


def handle_open(email_id: str, recipient: str):
    """Handle email open event"""
    print(f"[OPEN] {recipient} opened email {email_id}")
    # Could trigger follow-up SMS or call here


def handle_click(email_id: str, recipient: str, link: str):
    """Handle email click event"""
    print(f"[CLICK] {recipient} clicked {link}")
    # High intent signal - could trigger immediate call


def handle_bounce(email_id: str, recipient: str):
    """Handle email bounce event"""
    print(f"[BOUNCE] Email to {recipient} bounced")
    # Remove from future campaigns


def get_tracking_stats():
    """Get email tracking statistics"""
    try:
        with open(TRACKING_LOG, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    
    stats = {
        "total_events": len(logs),
        "opens": len([l for l in logs if l.get('event') == 'email.opened']),
        "clicks": len([l for l in logs if l.get('event') == 'email.clicked']),
        "bounces": len([l for l in logs if l.get('event') == 'email.bounced']),
        "delivered": len([l for l in logs if l.get('event') == 'email.delivered'])
    }
    
    if stats['delivered'] > 0:
        stats['open_rate'] = f"{(stats['opens'] / stats['delivered']) * 100:.1f}%"
        stats['click_rate'] = f"{(stats['clicks'] / stats['delivered']) * 100:.1f}%"
    
    return stats


@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(get_tracking_stats())


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "email-tracking"})


if __name__ == "__main__":
    print("Starting Email Tracking Webhook Server...")
    print("To use: Configure Resend webhook to POST to /webhook/resend")
    app.run(host='0.0.0.0', port=5051, debug=True)
