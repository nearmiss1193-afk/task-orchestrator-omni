"""
GCP Cloud Run Backup Deployment
===============================
Minimal Flask app that runs the same jobs as Modal when Modal is down.
Deploy to Cloud Run as a backup.

Deploy command:
    gcloud run deploy empire-backup --source . --region us-east1 --allow-unauthenticated
"""
import os
import json
import requests
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# === CREDENTIALS ===
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RESEND_KEY = os.getenv("RESEND_API_KEY")
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
APOLLO_KEY = os.getenv("APOLLO_API_KEY")


def get_supabase():
    """Get Supabase client."""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "provider": "gcp-cloud-run",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/vapi-callback", methods=["POST"])
def vapi_callback():
    """Handle Vapi webhooks (backup for Modal)."""
    data = request.get_json()
    call_status = data.get("message", {}).get("type", "unknown")
    
    print(f"[GCP BACKUP] Vapi webhook: {call_status}")
    
    # Log to Supabase
    try:
        client = get_supabase()
        if call_status == "end-of-call-report":
            msg = data.get("message", {})
            client.table("call_transcripts").upsert({
                "call_id": msg.get("call", {}).get("id"),
                "phone_number": msg.get("customer", {}).get("number"),
                "transcript": msg.get("transcript", ""),
                "summary": msg.get("summary", ""),
                "metadata": msg
            }).execute()
    except Exception as e:
        print(f"[GCP BACKUP] Error: {e}")
    
    return jsonify({"status": "received"})


@app.route("/email-callback", methods=["POST"])
def email_callback():
    """Handle Resend email webhooks (backup for Modal)."""
    data = request.get_json()
    event_type = data.get("type", "unknown")
    
    print(f"[GCP BACKUP] Email webhook: {event_type}")
    
    return jsonify({"status": "received", "event": event_type})


@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks (backup for Modal)."""
    data = request.get_json()
    event_type = data.get("type", "unknown")
    
    print(f"[GCP BACKUP] Stripe webhook: {event_type}")
    
    # Handle checkout completed
    if event_type == "checkout.session.completed":
        session = data.get("data", {}).get("object", {})
        email = session.get("customer_email")
        
        try:
            client = get_supabase()
            client.table("system_logs").insert({
                "level": "INFO",
                "event_type": "PAYMENT_RECEIVED",
                "message": f"Payment from {email}",
                "metadata": session
            }).execute()
        except:
            pass
    
    return jsonify({"status": "received"})


@app.route("/run-prospector", methods=["POST"])
def run_prospector():
    """Manually trigger prospector (backup for Modal cron)."""
    import re
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    cities = ["Tampa", "Orlando", "Miami"]
    target = cities[datetime.now().hour % len(cities)]
    
    prompt = f"Find 3 REAL HVAC companies in {target}, FL. Return JSON array with company_name, phone, city."
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if json_match:
            leads = json.loads(json_match.group())
            client = get_supabase()
            added = 0
            
            for lead in leads:
                try:
                    lead["status"] = "new"
                    lead["source"] = "gcp_backup"
                    client.table("leads").insert(lead).execute()
                    added += 1
                except:
                    pass
            
            return jsonify({"added": added, "city": target})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"added": 0})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
