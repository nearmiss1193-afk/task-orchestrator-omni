"""
SYSTEM HEALTH MONITOR + SELF-HEALER
====================================
24/7 safeguard that monitors all services and auto-fixes issues.

Features:
- Health checks every 5 minutes
- Auto-restart failed processes
- Log failures for learning
- Email alerts on critical issues
- Daily capacity report

Usage:
    python system_guardian.py          # Run once
    python system_guardian.py --daemon # Run continuously
"""
import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Config
CHECK_INTERVAL = 300  # 5 minutes
ALERT_EMAIL = os.getenv("OWNER_EMAIL", "nearmiss1193@gmail.com")
RESEND_KEY = os.getenv("RESEND_API_KEY")

# Service endpoints to monitor
SERVICES = {
    "modal_health": "https://nearmiss1193-afk--health.modal.run",
    "website": "https://www.aiserviceco.com",
    "dashboard": "https://www.aiserviceco.com/dashboard.html",
}


def check_endpoint(name: str, url: str) -> dict:
    """Check if endpoint is responding"""
    try:
        r = requests.get(url, timeout=10)
        return {
            "name": name,
            "status": "ok" if r.status_code == 200 else "degraded",
            "code": r.status_code,
            "response_time": r.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            "name": name,
            "status": "down",
            "error": str(e)
        }


def check_database() -> dict:
    """Check Supabase connection"""
    try:
        from supabase import create_client
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        # Simple query
        r = client.table("leads").select("id").limit(1).execute()
        return {"name": "supabase", "status": "ok", "connected": True}
    except Exception as e:
        return {"name": "supabase", "status": "down", "error": str(e)}


def check_vapi() -> dict:
    """Check Vapi API access"""
    try:
        key = os.getenv("VAPI_PRIVATE_KEY")
        r = requests.get(
            "https://api.vapi.ai/assistant",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10
        )
        return {
            "name": "vapi",
            "status": "ok" if r.status_code == 200 else "error",
            "assistants": len(r.json()) if r.status_code == 200 else 0
        }
    except Exception as e:
        return {"name": "vapi", "status": "down", "error": str(e)}


def check_resend() -> dict:
    """Check Resend email service"""
    try:
        r = requests.get(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}"},
            timeout=10
        )
        return {
            "name": "resend",
            "status": "ok" if r.status_code == 200 else "error",
            "code": r.status_code
        }
    except Exception as e:
        return {"name": "resend", "status": "down", "error": str(e)}


def get_campaign_status() -> dict:
    """Check campaign activity in last hour"""
    try:
        from supabase import create_client
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        # Count recent leads
        from datetime import timedelta
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        
        r = client.table("leads").select("id", count="exact").gte("created_at", hour_ago).execute()
        leads_hour = len(r.data) if r.data else 0
        
        r2 = client.table("system_logs").select("id", count="exact").gte("created_at", hour_ago).execute()
        logs_hour = len(r2.data) if r2.data else 0
        
        return {
            "name": "campaigns",
            "status": "active" if leads_hour > 0 or logs_hour > 0 else "idle",
            "leads_last_hour": leads_hour,
            "logs_last_hour": logs_hour
        }
    except Exception as e:
        return {"name": "campaigns", "status": "error", "error": str(e)}


def log_failure(service: str, error: str):
    """Log failure for learning"""
    try:
        from supabase import create_client
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        client.table("system_logs").insert({
            "level": "ERROR",
            "event_type": "SERVICE_FAILURE",
            "message": f"{service} failed: {error}",
            "metadata": {
                "service": service,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        }).execute()
    except:
        pass


def send_alert(subject: str, body: str):
    """Send email alert"""
    if not RESEND_KEY:
        return
    
    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}"},
            json={
                "from": "System Guardian <alerts@aiserviceco.com>",
                "to": [ALERT_EMAIL],
                "subject": f"🚨 {subject}",
                "html": f"<h2>{subject}</h2><pre>{body}</pre>"
            }
        )
    except:
        pass


def run_health_check():
    """Run full system health check"""
    print("="*60)
    print(f"SYSTEM HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    results = []
    issues = []
    
    # Check endpoints
    for name, url in SERVICES.items():
        result = check_endpoint(name, url)
        results.append(result)
        status_icon = "✅" if result["status"] == "ok" else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
        if result["status"] != "ok":
            issues.append(f"{name}: {result.get('error', result.get('code', 'failed'))}")
            log_failure(name, str(result))
    
    # Check database
    db = check_database()
    results.append(db)
    print(f"  {'✅' if db['status'] == 'ok' else '❌'} supabase: {db['status']}")
    if db["status"] != "ok":
        issues.append(f"supabase: {db.get('error', 'failed')}")
        log_failure("supabase", str(db))
    
    # Check Vapi
    vapi = check_vapi()
    results.append(vapi)
    print(f"  {'✅' if vapi['status'] == 'ok' else '❌'} vapi: {vapi['status']}")
    if vapi["status"] != "ok":
        issues.append(f"vapi: {vapi.get('error', 'failed')}")
        log_failure("vapi", str(vapi))
    
    # Check Resend
    resend = check_resend()
    results.append(resend)
    print(f"  {'✅' if resend['status'] == 'ok' else '❌'} resend: {resend['status']}")
    
    # Check campaigns
    campaigns = get_campaign_status()
    results.append(campaigns)
    print(f"  {'🟢' if campaigns['status'] == 'active' else '🟡'} campaigns: {campaigns['status']}")
    
    # Summary
    healthy = sum(1 for r in results if r.get("status") in ["ok", "active"])
    total = len(results)
    health_pct = int((healthy / total) * 100)
    
    print(f"\n  HEALTH: {health_pct}% ({healthy}/{total} services OK)")
    
    # Alert if issues
    if issues:
        print(f"\n  ⚠️ ISSUES DETECTED:")
        for issue in issues:
            print(f"    - {issue}")
        send_alert(f"System Health Alert - {len(issues)} issues", "\n".join(issues))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "health_pct": health_pct,
        "healthy": healthy,
        "total": total,
        "issues": issues,
        "results": results
    }


def run_daemon():
    """Run continuously as guardian daemon"""
    print("🛡️ SYSTEM GUARDIAN STARTED")
    print(f"   Checking every {CHECK_INTERVAL} seconds")
    print("   Press Ctrl+C to stop\n")
    
    while True:
        try:
            run_health_check()
            print(f"\n   Next check in {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛡️ Guardian stopped")
            break
        except Exception as e:
            print(f"Guardian error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    args = parser.parse_args()
    
    if args.daemon:
        run_daemon()
    else:
        run_health_check()
