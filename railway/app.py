"""
RAILWAY CLOUD WORKER
====================
Full autonomous outreach system running 24/7 on Railway.
Combines: Prospecting, Outreach, Inbound Response
"""
import os
import time
import json
import random
import requests
import schedule
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread
from brain import EmpireBrain

app = Flask(__name__)
brain = EmpireBrain()

# ==== CONFIG ====
APOLLO_KEY = os.environ.get("APOLLO_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") 
VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
GHL_API_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"

SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"
BACKUP_PHONE = "+13529368152"

NICHES = [
    {"keywords": "HVAC contractor", "location": "Florida"},
    {"keywords": "Plumbing services", "location": "Texas"},
    {"keywords": "Roofing company", "location": "Georgia"},
    {"keywords": "Electrical contractor", "location": "Arizona"},
]

stats = {
    "prospects": 0, 
    "emails": 0, 
    "sms": 0, 
    "calls": 0, 
    "last_heartbeat": time.time()
}

# ==== SUPABASE ====
def supabase_request(method, table, data=None, params=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k,v in params.items()])
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=30)
        return r.json() if r.ok else None
    except:
        return None

# ==== PROSPECTOR ====
def prospect_niche(niche):
    """Find leads using Apollo API"""
    global stats
    if not APOLLO_KEY:
        print("[PROSPECT] No Apollo key")
        return 0
    
    print(f"[PROSPECT] Searching: {niche['keywords']} in {niche['location']}")
    
    try:
        r = requests.post(
            "https://api.apollo.io/v1/organizations/search",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": APOLLO_KEY
            },
            json={
                "q_keywords": niche["keywords"],
                "organization_locations": [niche["location"]],
                "organization_num_employees_ranges": ["1,50"],
                "per_page": 10
            },
            timeout=60
        )
        
        if r.status_code == 429:
            print("[PROSPECT] Rate limited")
            return 0
        
        if r.ok:
            companies = r.json().get("organizations", [])
            saved = 0
            for company in companies:
                lead = {
                    "company_name": company.get("name"),
                    "website_url": company.get("website_url"),
                    "phone": company.get("phone"),
                    "city": company.get("city"),
                    "state": company.get("state"),
                    "status": "new",
                    "source": "railway_cloud"
                }
                # Save to Supabase
                result = supabase_request("POST", "leads", lead)
                if result:
                    saved += 1
            stats["prospects"] += saved
            print(f"[PROSPECT] Saved {saved} leads")
            return saved
    except Exception as e:
        print(f"[PROSPECT] Error: {e}")
    return 0

def run_prospector():
    """Run prospector based on Learned Strategy"""
    print(f"\n[{datetime.now().strftime('%H:%M')}] PROSPECTOR RUNNING (AI CONTROLLED)")
    
    # Brain decides which niche to target
    best_niche_key = brain.get_strategy()
    niche_config = brain.get_assets(best_niche_key)
    
    # Map back to API format
    target_niche = {
        "keywords": niche_config["keywords"],
        "location": niche_config["location"] 
    }
    
    saved = prospect_niche(target_niche)
    
    # Log learning
    if saved > 0:
        brain.record_outcome("prospecting_success", best_niche_key, {"count": saved})

# ==== OUTREACH ====
def send_email(email, company, name):
    """Send outreach email via GHL webhook"""
    global stats
    html = f"""
    <p>Hi {name or 'there'},</p>
    <p>Quick question about <b>{company}</b> - are you still fielding after-hours calls yourself?</p>
    <p>We built an AI phone agent that answers 24/7, books jobs, and never misses a call. 
    <b>14-Day Free Trial</b>, no credit card needed.</p>
    <p>Worth a quick look? <a href="https://aiserviceco.com">See Demo</a></p>
    <p>- Daniel, AI Service Co<br>(352) 758-5336</p>
    """
    try:
        r = requests.post(GHL_EMAIL, json={
            "email": email,
            "from_name": "Daniel",
            "from_email": "daniel@aiserviceco.com",
            "subject": f"Quick question for {company}",
            "html_body": html
        }, timeout=15)
        if r.ok:
            stats["emails"] += 1
            print(f"[EMAIL] Sent to {email}")
            return True
    except:
        pass
    return False

def send_sms(phone, message):
    """Send SMS via GHL webhook"""
    global stats
    try:
        r = requests.post(GHL_SMS, json={"phone": phone, "message": message}, timeout=15)
        if r.ok:
            stats["sms"] += 1
            print(f"[SMS] Sent to {phone}")
            return True
    except:
        pass
    return False

def trigger_call(phone, name):
    """Trigger Vapi outbound call"""
    global stats
    try:
        r = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": PHONE_ID,
                "assistantId": SARAH_ID,
                "customer": {"number": phone, "name": name}
            },
            timeout=30
        )
        if r.ok:
            stats["calls"] += 1
            print(f"[CALL] Initiated to {phone}")
            return True
    except:
        pass
    return False

def run_outreach():
    """Contact new leads"""
    print(f"\n[{datetime.now().strftime('%H:%M')}] OUTREACH RUNNING")
    
    # Get uncontacted leads
    leads = supabase_request("GET", "leads", params={"status": "eq.new", "limit": "5"})
    
    if not leads:
        print("[OUTREACH] No new leads")
        return
    
    for lead in leads:
        company = lead.get("company_name", "Business")
        email = lead.get("email")
        phone = lead.get("phone")
        
        # Send email if available
        if email:
            send_email(email, company, lead.get("decision_maker"))
        
        # Send SMS if phone available
        if phone:
            msg = f"Hi! Quick question about {company} - are you handling after-hours calls? We have a 14-day free trial for AI phone answering. Interest? -Sarah, AI Service Co"
            send_sms(phone, msg)
        
        # Mark as contacted
        supabase_request("PATCH", f"leads?id=eq.{lead['id']}", {"status": "contacted"})
    
    print(f"[OUTREACH] Processed {len(leads)} leads")

# ==== SCHEDULER ====
def run_scheduler():
    """Background scheduler thread"""
    schedule.every(2).hours.do(run_prospector)
    schedule.every(1).hours.do(run_outreach)
    schedule.every(6).hours.do(send_status_report)
    
    # Run immediately on start
    run_prospector()
    run_outreach()
    
    while True:
        schedule.run_pending()
        stats["last_heartbeat"] = time.time()
        time.sleep(60)

def send_status_report():
    """Send status report to owner"""
    html = f"""
    <h2>Railway Cloud Worker Status</h2>
    <p>Time: {datetime.utcnow().isoformat()}</p>
    <p>Prospects found: {stats['prospects']}</p>
    <p>Emails sent: {stats['emails']}</p>
    <p>SMS sent: {stats['sms']}</p>
    <p>Calls made: {stats['calls']}</p>
    """
    try:
        requests.post(GHL_EMAIL, json={
            "email": "owner@aiserviceco.com",
            "from_name": "Railway Cloud",
            "from_email": "system@aiserviceco.com",
            "subject": f"[STATUS] E:{stats['emails']} S:{stats['sms']} C:{stats['calls']}",
            "html_body": html
        }, timeout=15)
    except:
        pass

# ==== WEB ENDPOINTS ====
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "empire-railway-worker",
        "stats": stats,
        "uptime": datetime.utcnow().isoformat()
    })

@app.route("/health")
def health():
    # Deep Health Check: Ensure worker thread is alive (heartbeat within 5 mins)
    if time.time() - stats.get("last_heartbeat", 0) > 300:
        return jsonify({"status": "unhealthy", "reason": "thread_dead"}), 500
    return jsonify({"status": "healthy"})

@app.route("/trigger/prospect", methods=["POST"])
def api_prospect():
    run_prospector()
    return jsonify({"status": "triggered"})

@app.route("/trigger/outreach", methods=["POST"])
def api_outreach():
    run_outreach()
    return jsonify({"status": "triggered"})

@app.route("/vapi/webhook", methods=["POST"])
def vapi_webhook():
    """Handle Vapi webhooks"""
    data = request.json
    msg_type = data.get("message", {}).get("type", "unknown")
    print(f"[VAPI] {msg_type}")
    
    if msg_type == "assistant-request":
        return jsonify({"assistantId": SARAH_ID})
    
    if msg_type == "end-of-call-report":
        ended = data.get("message", {}).get("endedReason", "")
        if ended in ["no-answer", "failed", "voicemail"]:
            customer = data.get("message", {}).get("call", {}).get("customer", {}).get("number")
            if customer:
                send_sms(BACKUP_PHONE, f"MISSED: {customer} - {ended}")
    
    return jsonify({"status": "received"})

if __name__ == "__main__":
    print("="*50)
    print("EMPIRE RAILWAY WORKER STARTING")
    print("="*50)
    
    # Start scheduler in background
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run Flask server
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
