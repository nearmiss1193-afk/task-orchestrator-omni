
# SOVEREIGN ENGINE v11.0 - PRODUCTION CORE
import os, time, json, requests, sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)

# ==== STABILITY PROTOCOL: MONOLITHIC CONFIG ====
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
# ==== SOVEREIGN VAULT: PERSISTENCE PROTOCOL ====
BRIDGE_TOKEN = os.environ.get("EXTERNAL_BRIDGE_TOKEN") or "sov-audit-2026-ghost"
EXTERNAL_BRIDGE_URL = "https://empire-unified-backup-production-6d15.up.railway.app"
# Recovery Logic: Ensure handshake never drops
if not os.environ.get("EXTERNAL_BRIDGE_TOKEN"):
    print(f"🛰️ [Vault] Restoring handshake via hardcoded token: {BRIDGE_TOKEN[:10]}...")

def supabase_request(method, table, params=None, json_data=None):
    if not SUPABASE_KEY:
        return None
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    try:
        if method == "GET":
            res = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=json_data)
        elif method == "PATCH":
            res = requests.patch(url, headers=headers, json=json_data, params=params)
        
        if res.status_code in [200, 201]:
            try: return res.json()
            except: return {"status": "success"}
        return None
    except Exception as e:
        print(f"[Supabase Error] {e}")
        return None

# ==== AUTHENTICATION DECORATOR ====
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Sovereign-Token')
        if not token or token != BRIDGE_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ==== BRIDGE ENDPOINTS (PHASE 13) ====
@app.route("/bridge/performance", methods=["GET"])
@require_auth
def bridge_performance():
    leads = supabase_request("GET", "contacts_master", params={"select": "status"})
    touches = supabase_request("GET", "outbound_touches", params={"order": "ts.desc", "limit": "20"})
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "funnel": {
            "total_leads": len(leads) if leads else 0,
            "outreach_active": len([l for l in leads if l.get('status') in ['contacted', 'emailed', 'sms_sent']]) if leads else 0,
            "positive_responses": len([l for l in leads if l.get('status') in ['interested', 'positive', 'hot']]) if leads else 0
        },
        "recent_activity": []
    }
    if touches:
        for t in touches[:10]:
            summary["recent_activity"].append({
                "ts": t.get("ts"), "channel": t.get("channel"), "status": t.get("status"), "company": t.get("lead_name") or "Unknown"
            })
    return jsonify(summary)

@app.route("/bridge/task", methods=["POST"])
@require_auth
def bridge_task():
    data = request.json
    task_desc = data.get("task")
    if not task_desc: return jsonify({"error": "Missing task"}), 400
    
    res = supabase_request("POST", "sovereign_tasks", json_data={
        "task_description": task_desc,
        "model_source": data.get("source", "External-Audit"),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    })
    return jsonify({"status": "Task Received", "task_id": res[0].get('id') if res else "unknown"})

@app.route("/bridge/instructions", methods=["POST"])
@require_auth
def bridge_instructions():
    data = request.json
    instructions = data.get("instructions")
    if not instructions: return jsonify({"error": "Missing instructions"}), 400
    
    supabase_request("PATCH", "system_state", 
                     params={"key": "eq.audit_instructions"},
                     json_data={"value": instructions, "updated_at": datetime.now().isoformat()})
    return jsonify({"status": "Instructions Updated"})

# ==== CORE APP LOGIC ====
stats = {"emails": 0, "sms": 0, "calls": 0, "last_heartbeat": time.time()}

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "version": "v11.6-monolithic",
        "heartbeat_age": time.time() - stats["last_heartbeat"],
        "supabase_online": SUPABASE_KEY is not None
    })

@app.route("/dashboard_stats", methods=["GET"])
@app.route("/stats", methods=["GET"])
@app.route("/sovereign_intel_v1", methods=["GET"])
def get_dashboard_stats():
    try:
        leads = supabase_request("GET", "contacts_master", params={"select": "status"})
        funnel = {"prospects_discovered": 0, "outreach_dispatched": 0, "replied": 0, "interested": 0, "booked": 0}
        
        if leads:
            funnel["prospects_discovered"] = len(leads)
            funnel["outreach_dispatched"] = len([l for l in leads if l.get('status') in ['contacted', 'emailed', 'sms_sent', 'research_done']])
            funnel["interested"] = len([l for l in leads if l.get('status') in ['interested', 'positive', 'hot']])
            funnel["booked"] = len([l for l in leads if l.get('status') == 'booked'])
            funnel["replied"] = len([l for l in leads if l.get('status') in ['interested', 'booked', 'replied', 'negative']])

        touches = supabase_request("GET", "outbound_touches", params={"order": "ts.desc", "limit": "15"})
        recent_comms = []
        if touches:
            for t in touches:
                recent_comms.append({"ts": t.get("ts"), "company": t.get("lead_name") or f"Lead {t.get('contact_id', '???')}", "channel": t.get("channel", "comm"), "status": f"Sent {t.get('channel', 'touch')}"})
        else:
            recent_comms = [{"ts": datetime.now().isoformat(), "company": "Sovereign Engine", "channel": "sys", "status": "No recent touches"}]

        return jsonify({
            "sentinel_score": 100, "mode": "working", "pipeline_value": funnel["interested"] * 297, "outreach_burn": (stats["emails"] * 0.005), 
            "funnel": funnel, "recent_comms": recent_comms, "server_time": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("public", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
