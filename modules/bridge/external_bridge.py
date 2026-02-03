
import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps

# Setup Blueprint
bridge_bp = Blueprint('bridge', __name__)

# SECURITY: The Sovereign Token
# This must be provided in the X-Sovereign-Token header.
BRIDGE_TOKEN = os.environ.get("EXTERNAL_BRIDGE_TOKEN") or "sov-audit-2026-ghost"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Sovereign-Token')
        if not token or token != BRIDGE_TOKEN:
            return jsonify({"error": "Unauthorized. Invalid Sovereign Token."}), 401
        return f(*args, **kwargs)
    return decorated

from modules.database.db_utils import supabase_request

@bridge_bp.route("/performance", methods=["GET"])
@require_auth
def get_performance_summary():
    """
    Summarize performance data for external audit.
    Fetches real-time counts from contacts_master and outbound_touches.
    """
    
    # 1. Funnel Snapshot
    leads = supabase_request("GET", "contacts_master", params={"select": "status"})
    touches = supabase_request("GET", "outbound_touches", params={"order": "ts.desc", "limit": "50"})
    
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
                "ts": t.get("ts"),
                "channel": t.get("channel"),
                "status": t.get("status"),
                "company": t.get("lead_name") or "Unknown"
            })
            
    return jsonify(summary)

@bridge_bp.route("/task", methods=["POST"])
@require_auth
def accept_task():
    """
    Accept an external task from OpenAI/Grok.
    Saves to the sovereign_tasks table.
    """
    data = request.json
    task_desc = data.get("task")
    source = data.get("source", "External-Audit")
    
    if not task_desc:
        return jsonify({"error": "Missing task description"}), 400
        
    supabase_request = get_supabase()
    res = supabase_request("POST", "sovereign_tasks", json_data={
        "task_description": task_desc,
        "model_source": source,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    })
    
    return jsonify({"status": "Task Received", "task_id": res[0].get('id') if res else "unknown"})

@bridge_bp.route("/instructions", methods=["POST"])
@require_auth
def relay_instructions():
    """
    Relay updated system instructions (overrides/prompts).
    Updates system_state table.
    """
    data = request.json
    instructions = data.get("instructions")
    
    if not instructions:
        return jsonify({"error": "Missing instructions content"}), 400
        
    supabase_request = get_supabase()
    # Using the system_state table to store current directive
    res = supabase_request("PATCH", "system_state", 
                           params={"key": "eq.audit_instructions"},
                           json_data={"value": instructions, "updated_at": datetime.now().isoformat()})
    
    return jsonify({"status": "Instructions Updated", "applied_at": datetime.now().isoformat()})
