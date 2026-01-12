"""
EMPIRE SELF-HEALING HEALTH MONITOR
==================================
Automated system that checks all critical functions and repairs issues.
Runs every 30 minutes to ensure the business never stops.

Features:
- Checks Modal function status
- Verifies Supabase connectivity
- Tests API endpoints
- Sends alerts on failures
- Auto-repairs common issues (schema cache, etc.)
"""
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ALERT_EMAIL = "owner@aiserviceco.com"

# Health check endpoints
HEALTH_CHECKS = {
    "modal_webhook": "https://nearmiss1193-afk--empire-sovereign-v2-email-webhook.modal.run",
    "website": "https://aiserviceco.com",
}

# Critical tables to verify
CRITICAL_TABLES = [
    "prospects",
    "email_logs", 
    "system_logs",
    "call_logs",
]


def log_health_event(event_type: str, details: dict, status: str = "healthy"):
    """Log health check to Supabase"""
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        supabase.table("system_logs").insert({
            "event_type": f"HEALTH_{event_type.upper()}",
            "details": {
                **details,
                "status": status,
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {"monitor": "self-healing"}
        }).execute()
    except Exception as e:
        print(f"⚠️ Failed to log health event: {e}")


def send_alert(subject: str, message: str):
    """Send email alert when issues detected"""
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        
        resend.Emails.send({
            "from": "Health Monitor <monitor@aiserviceco.com>",
            "to": [ALERT_EMAIL],
            "subject": f"🚨 Empire Alert: {subject}",
            "html": f"""
            <div style="font-family: system-ui; padding: 20px; background: #1e293b; color: #f8fafc;">
                <h2 style="color: #ef4444;">⚠️ System Alert</h2>
                <p>{message}</p>
                <hr style="border-color: #334155;">
                <p style="color: #64748b; font-size: 12px;">
                    Sent by Empire Health Monitor at {datetime.now().isoformat()}
                </p>
            </div>
            """
        })
        print(f"📧 Alert sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")


def check_supabase_health():
    """Verify Supabase connectivity and schema"""
    print("\n🔍 Checking Supabase health...")
    issues = []
    
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check each critical table
        for table in CRITICAL_TABLES:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table}: OK")
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ {table}: {error_msg[:50]}")
                issues.append({"table": table, "error": error_msg})
                
                # Auto-repair: If schema cache issue, refresh it
                if "PGRST" in error_msg:
                    print(f"   🔧 Attempting schema cache refresh...")
                    try:
                        supabase.rpc("pg_notify", {"channel": "pgrst", "payload": "reload schema"}).execute()
                        print(f"   ✅ Schema cache refresh triggered")
                    except:
                        # Direct SQL approach
                        pass
        
        if issues:
            log_health_event("SUPABASE", {"issues": issues}, "warning")
            return False, issues
        else:
            log_health_event("SUPABASE", {"tables_checked": len(CRITICAL_TABLES)}, "healthy")
            return True, []
            
    except Exception as e:
        log_health_event("SUPABASE", {"error": str(e)}, "critical")
        return False, [{"error": str(e)}]


def check_endpoints():
    """Verify all critical endpoints are responding"""
    print("\n🌐 Checking endpoints...")
    issues = []
    
    for name, url in HEALTH_CHECKS.items():
        try:
            # Quick timeout check
            response = requests.get(url, timeout=10)
            if response.status_code < 500:
                print(f"   ✅ {name}: {response.status_code}")
            else:
                print(f"   ❌ {name}: {response.status_code}")
                issues.append({"endpoint": name, "status": response.status_code})
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:40]}")
            issues.append({"endpoint": name, "error": str(e)[:100]})
    
    if issues:
        log_health_event("ENDPOINTS", {"issues": issues}, "warning")
    else:
        log_health_event("ENDPOINTS", {"checked": len(HEALTH_CHECKS)}, "healthy")
    
    return len(issues) == 0, issues


def check_recent_activity():
    """Verify the system is actively working"""
    print("\n📊 Checking recent activity...")
    
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check for logs in last 2 hours
        two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()
        
        result = supabase.table("system_logs").select("*").gte("created_at", two_hours_ago).execute()
        log_count = len(result.data)
        
        if log_count > 0:
            print(f"   ✅ {log_count} system events in last 2 hours")
            log_health_event("ACTIVITY", {"event_count": log_count, "period": "2h"}, "healthy")
            return True, []
        else:
            print(f"   ⚠️ No activity in last 2 hours - system may be stalled")
            log_health_event("ACTIVITY", {"event_count": 0, "period": "2h"}, "warning")
            return False, [{"issue": "No activity in 2 hours"}]
            
    except Exception as e:
        print(f"   ❌ Activity check failed: {e}")
        return False, [{"error": str(e)}]


def run_full_health_check():
    """Run complete health check with alerts"""
    print("=" * 60)
    print("🏥 EMPIRE SELF-HEALING HEALTH MONITOR")
    print(f"   Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_healthy = True
    all_issues = []
    
    # 1. Check Supabase
    healthy, issues = check_supabase_health()
    if not healthy:
        all_healthy = False
        all_issues.extend(issues)
    
    # 2. Check endpoints
    healthy, issues = check_endpoints()
    if not healthy:
        all_healthy = False
        all_issues.extend(issues)
    
    # 3. Check activity
    healthy, issues = check_recent_activity()
    if not healthy:
        all_healthy = False
        all_issues.extend(issues)
    
    # Summary
    print("\n" + "=" * 60)
    if all_healthy:
        print("✅ ALL SYSTEMS HEALTHY")
    else:
        print(f"⚠️ {len(all_issues)} ISSUE(S) DETECTED")
        
        # Send alert email
        issue_summary = "\n".join([f"• {json.dumps(i)}" for i in all_issues[:5]])
        send_alert(
            f"{len(all_issues)} Issues Detected",
            f"<pre>{issue_summary}</pre><br/>Please check the system."
        )
    
    print("=" * 60)
    return all_healthy, all_issues


if __name__ == "__main__":
    run_full_health_check()
