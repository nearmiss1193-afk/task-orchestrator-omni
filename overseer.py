# --- DIRECTIVE ---
# Tech Stack: Modal, Supabase, GHL API
# Goal: External watchdog monitoring Empire system health
# Mission: Observe, Report, Alert

import modal
import os
import json
import requests
import datetime
from supabase import create_client, Client

app = modal.App("empire-overseer")

image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "requests", "fastapi")
)

VAULT = modal.Secret.from_name("agency-vault")

# --- HELPERS ---

def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def send_alert(subject: str, body: str, alert_type: str = "Email"):
    """Send alert via GHL to owner"""
    owner_contact_id = "2uuVuOP0772z7hay16og"
    ghl_token = os.environ.get("GHL_API_TOKEN")
    headers = {
        'Authorization': f'Bearer {ghl_token}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    payload = {
        "type": alert_type,
        "contactId": owner_contact_id,
        "emailFrom": "overseer@aiserviceco.com",
        "emailSubject": subject,
        "html": body if alert_type == "Email" else None,
        "message": body if alert_type == "SMS" else None
    }
    try:
        requests.post("https://services.leadconnectorhq.com/conversations/messages", 
                      json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"[Overseer] Alert failed: {e}")

def log_overseer(message: str):
    """Log to Supabase brain_logs"""
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {message}")
    try:
        supabase = get_supabase()
        supabase.table("brain_logs").insert({
            "message": f"[OVERSEER] {message}",
            "timestamp": timestamp
        }).execute()
    except:
        pass

# --- CORE MONITORING FUNCTIONS ---

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(minutes=30))
def health_check():
    """
    MISSION: SYSTEM HEALTH WATCHDOG
    Runs every 30 minutes to verify system is alive.
    """
    log_overseer("🔭 Health Check starting...")
    issues = []
    
    # 1. Check Supabase connectivity
    try:
        supabase = get_supabase()
        res = supabase.table("brain_logs").select("id").limit(1).execute()
        log_overseer("✅ Supabase: CONNECTED")
    except Exception as e:
        issues.append(f"❌ Supabase DOWN: {str(e)}")
        log_overseer(f"❌ Supabase: FAILED - {e}")
    
    # 2. Check GHL API connectivity
    try:
        ghl_token = os.environ.get("GHL_API_TOKEN")
        res = requests.get(
            "https://services.leadconnectorhq.com/locations/v2/me",
            headers={'Authorization': f'Bearer {ghl_token}', 'Version': '2021-04-15'},
            timeout=10
        )
        if res.status_code == 200:
            log_overseer("✅ GHL API: CONNECTED")
        else:
            issues.append(f"⚠️ GHL API returned {res.status_code}")
    except Exception as e:
        issues.append(f"❌ GHL API DOWN: {str(e)}")
        log_overseer(f"❌ GHL API: FAILED - {e}")
    
    # 3. Ping main system endpoint
    try:
        main_url = "https://nearmiss1193-afk--ghl-omni-automation-heartbeat-ping.modal.run"
        res = requests.get(main_url, timeout=15)
        if res.status_code == 200:
            log_overseer("✅ Main System: ALIVE")
        else:
            issues.append(f"⚠️ Main System returned {res.status_code}")
    except Exception as e:
        issues.append(f"❌ Main System UNREACHABLE: {str(e)}")
        log_overseer(f"❌ Main System: UNREACHABLE - {e}")
    
    # 4. Check for stuck staged replies
    try:
        supabase = get_supabase()
        cutoff = (datetime.datetime.now() - datetime.timedelta(hours=6)).isoformat()
        stuck = supabase.table("staged_replies").select("id").eq("status", "pending_approval").lt("created_at", cutoff).execute()
        if stuck.data and len(stuck.data) > 0:
            issues.append(f"⚠️ {len(stuck.data)} staged replies pending >6 hours")
    except:
        pass
    
    # Alert if issues found
    if issues:
        body = "<h1>🚨 Overseer Alert</h1><ul>"
        for issue in issues:
            body += f"<li>{issue}</li>"
        body += "</ul><p>Timestamp: " + datetime.datetime.now().isoformat() + "</p>"
        send_alert("🚨 Empire System Alert", body)
        log_overseer(f"⚠️ Health check found {len(issues)} issues, alert sent")
    else:
        log_overseer("✅ Health check complete: All systems operational")
    
    return {"status": "ok" if not issues else "issues_found", "issues": issues}

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=24))
def growth_audit():
    """
    MISSION: DAILY GROWTH METRICS
    Counts new leads, sent messages, and conversion progress.
    """
    log_overseer("📊 Growth Audit starting...")
    supabase = get_supabase()
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    
    # Count new leads
    new_leads = supabase.table("contacts_master").select("id", count="exact").gte("created_at", yesterday).execute()
    lead_count = new_leads.count or 0
    
    # Count by status
    statuses = {}
    for status in ["new", "research_done", "outreach_sent", "nurtured"]:
        res = supabase.table("contacts_master").select("id", count="exact").eq("status", status).execute()
        statuses[status] = res.count or 0
    
    # Count sent replies
    sent = supabase.table("staged_replies").select("id", count="exact").eq("status", "sent").gte("created_at", yesterday).execute()
    sent_count = sent.count or 0
    
    # Build report
    report = f"""
    <h1>📊 Empire Daily Growth Report</h1>
    <p><b>Report Date:</b> {datetime.date.today().isoformat()}</p>
    
    <h2>🌱 24-Hour Metrics</h2>
    <ul>
        <li><b>New Leads:</b> {lead_count}</li>
        <li><b>Messages Sent:</b> {sent_count}</li>
    </ul>
    
    <h2>📈 Pipeline Status</h2>
    <table border="1" style="border-collapse:collapse;">
        <tr><th>Status</th><th>Count</th></tr>
        <tr><td>New</td><td>{statuses.get('new', 0)}</td></tr>
        <tr><td>Research Done</td><td>{statuses.get('research_done', 0)}</td></tr>
        <tr><td>Outreach Sent</td><td>{statuses.get('outreach_sent', 0)}</td></tr>
        <tr><td>Nurtured</td><td>{statuses.get('nurtured', 0)}</td></tr>
    </table>
    
    <p style="color:gray;font-size:12px;">Generated by Empire Overseer</p>
    """
    
    send_alert("📊 Empire Daily Growth Report", report)
    log_overseer(f"✅ Growth audit complete: {lead_count} new leads, {sent_count} sent")
    
    return {"new_leads": lead_count, "sent": sent_count, "statuses": statuses}

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=24))
def evolution_tracker():
    """
    MISSION: LEARNING & EVOLUTION TRACKING
    Monitors error recovery and self-annealing events.
    """
    log_overseer("🧬 Evolution Tracker starting...")
    supabase = get_supabase()
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    
    # Count error logs
    errors = supabase.table("brain_logs").select("id", count="exact").ilike("message", "%ERR%").gte("timestamp", yesterday).execute()
    error_count = errors.count or 0
    
    # Count recovery logs
    recoveries = supabase.table("brain_logs").select("id", count="exact").ilike("message", "%retry%").gte("timestamp", yesterday).execute()
    recovery_count = recoveries.count or 0
    
    # Calculate learning ratio
    learning_score = "N/A"
    if error_count > 0:
        ratio = recovery_count / error_count
        if ratio > 0.8:
            learning_score = "🟢 Excellent (>80% recovery)"
        elif ratio > 0.5:
            learning_score = "🟡 Good (50-80% recovery)"
        else:
            learning_score = "🔴 Needs attention (<50% recovery)"
    else:
        learning_score = "🟢 No errors detected"
    
    report = f"""
    <h1>🧬 Empire Evolution Report</h1>
    <p><b>Learning Score:</b> {learning_score}</p>
    <ul>
        <li><b>Errors (24h):</b> {error_count}</li>
        <li><b>Recoveries (24h):</b> {recovery_count}</li>
    </ul>
    <p style="color:gray;font-size:12px;">Generated by Empire Overseer</p>
    """
    
    send_alert("🧬 Empire Evolution Report", report)
    log_overseer(f"✅ Evolution tracker: {error_count} errors, {recovery_count} recoveries")
    
    return {"errors": error_count, "recoveries": recovery_count, "score": learning_score}

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(days=7))
def expansion_meter():
    """
    MISSION: WEEKLY EXPANSION ANALYSIS
    Compares week-over-week growth trajectory.
    """
    log_overseer("🚀 Expansion Meter starting...")
    supabase = get_supabase()
    
    now = datetime.datetime.now()
    week_ago = (now - datetime.timedelta(days=7)).isoformat()
    two_weeks_ago = (now - datetime.timedelta(days=14)).isoformat()
    
    # This week
    this_week = supabase.table("contacts_master").select("id", count="exact").gte("created_at", week_ago).execute()
    this_count = this_week.count or 0
    
    # Last week
    last_week = supabase.table("contacts_master").select("id", count="exact").gte("created_at", two_weeks_ago).lt("created_at", week_ago).execute()
    last_count = last_week.count or 0
    
    # Calculate growth
    if last_count > 0:
        growth = ((this_count - last_count) / last_count) * 100
        growth_str = f"{growth:+.1f}%"
        if growth > 10:
            status = "🚀 EXPANDING"
        elif growth > 0:
            status = "📈 Growing"
        elif growth > -10:
            status = "⚠️ Stagnating"
        else:
            status = "🔴 Declining"
    else:
        growth_str = "N/A (no baseline)"
        status = "📊 First week"
    
    report = f"""
    <h1>🚀 Empire Weekly Expansion</h1>
    <p><b>Status:</b> {status}</p>
    <table border="1" style="border-collapse:collapse;">
        <tr><th>Period</th><th>New Leads</th></tr>
        <tr><td>This Week</td><td>{this_count}</td></tr>
        <tr><td>Last Week</td><td>{last_count}</td></tr>
        <tr><td><b>Growth</b></td><td><b>{growth_str}</b></td></tr>
    </table>
    <p style="color:gray;font-size:12px;">Generated by Empire Overseer</p>
    """
    
    send_alert("🚀 Empire Weekly Expansion Report", report)
    log_overseer(f"✅ Expansion meter: {growth_str} growth")
    
    return {"this_week": this_count, "last_week": last_count, "growth": growth_str, "status": status}

# --- MANUAL TRIGGERS ---

@app.function(image=image, secrets=[VAULT])
def run_all_checks():
    """Manual trigger to run all checks immediately"""
    log_overseer("🔧 Manual full audit triggered...")
    health_check.remote()
    growth_audit.remote()
    evolution_tracker.remote()
    expansion_meter.remote()
    return {"status": "all_checks_triggered"}

@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="GET")
def overseer_status():
    """HTTP endpoint to check overseer is running"""
    return {
        "status": "overseer_alive",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    app.run()
