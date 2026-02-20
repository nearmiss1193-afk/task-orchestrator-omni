"""
ERROR ALERTING SYSTEM
=====================
Notifies on 404 spikes, system errors, and critical failures.
Sends alerts via email (Resend) and logs to Supabase.

Usage:
    from modules.error_alerting import alert_on_error, check_for_spikes
    
    # Send immediate alert
    alert_on_error("404 SPIKE", "50 broken links detected in the last hour!")
    
    # Run spike checker (call periodically)
    check_for_spikes()
"""
import os
import requests
from datetime import datetime, timedelta
from supabase import create_client

# Config
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
ALERT_EMAIL = os.getenv("OWNER_EMAIL", "nearmiss1193@gmail.com")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

# Thresholds for alerting
ERROR_THRESHOLD_HOUR = 10  # Alert if >10 errors in 1 hour
ERROR_THRESHOLD_DAY = 50   # Alert if >50 errors in 24 hours


def get_client():
    """Get Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def send_email_alert(subject: str, body: str) -> bool:
    """Send alert email via Resend."""
    if not RESEND_API_KEY:
        print(f"[ALERT] No Resend key - would have sent: {subject}")
        return False
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Empire AI <alerts@aiserviceco.com>",
                "to": [ALERT_EMAIL],
                "subject": f"🚨 {subject}",
                "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; background: #1e293b; color: #f1f5f9;">
                    <h2 style="color: #ef4444;">⚠️ Alert: {subject}</h2>
                    <p style="color: #cbd5e1; white-space: pre-wrap;">{body}</p>
                    <hr style="border-color: #475569;">
                    <p style="color: #64748b; font-size: 12px;">
                        Empire AI Alert System · {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    </p>
                </div>
                """
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[ALERT] Failed to send email: {e}")
        return False


def log_error(error_type: str, message: str, metadata: dict = None) -> bool:
    """Log an error to the database."""
    try:
        client = get_client()
        
        client.table("system_logs").insert({
            "level": "ERROR",
            "event_type": error_type,
            "message": message,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return True
    except Exception as e:
        print(f"[ALERT] Failed to log error: {e}")
        return False


def alert_on_error(error_type: str, message: str, send_email: bool = True):
    """
    Handle an error - log it and optionally send alert.
    
    Args:
        error_type: Category of error (e.g., "404_SPIKE", "API_FAILURE", "CAMPAIGN_BLOCKED")
        message: Detailed error message
        send_email: Whether to send email alert immediately
    """
    print(f"[ALERT] {error_type}: {message}")
    
    # Always log to database
    log_error(error_type, message)
    
    # Send email for critical errors
    if send_email:
        send_email_alert(error_type, message)


def check_for_404_spikes() -> bool:
    """
    Check if there's been a spike in 404 errors.
    Returns True if spike detected (alert sent).
    """
    try:
        client = get_client()
        
        # Check last hour
        hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        result = client.table("click_events") \
            .select("*") \
            .eq("success", False) \
            .gte("created_at", hour_ago) \
            .execute()
        
        hour_errors = len(result.data)
        
        if hour_errors >= ERROR_THRESHOLD_HOUR:
            # Group by URL
            urls = {}
            for e in result.data:
                url = e.get("target_url", "unknown")
                urls[url] = urls.get(url, 0) + 1
            
            top_failures = sorted(urls.items(), key=lambda x: -x[1])[:5]
            
            message = f"""
Detected {hour_errors} failed clicks in the last hour!

Top failing URLs:
{chr(10).join(f'  [{count}x] {url}' for url, count in top_failures)}

Recommended action: Check these URLs and fix any broken links.
            """
            
            alert_on_error("404_SPIKE", message)
            return True
        
        return False
        
    except Exception as e:
        print(f"[ALERT] Spike check failed: {e}")
        return False


def check_for_spikes():
    """Run all spike detection checks."""
    print("[ALERT] Running spike detection...")
    
    spike_detected = check_for_404_spikes()
    
    if not spike_detected:
        print("[ALERT] No spikes detected ✓")
    
    return spike_detected


def get_error_summary(hours: int = 24) -> dict:
    """Get summary of recent errors."""
    try:
        client = get_client()
        
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        result = client.table("system_logs") \
            .select("*") \
            .eq("level", "ERROR") \
            .gte("created_at", since) \
            .execute()
        
        errors = result.data
        
        # Group by type
        by_type = {}
        for e in errors:
            t = e.get("event_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total": len(errors),
            "by_type": by_type,
            "recent": errors[:10]
        }
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("=" * 60)
    print("ERROR ALERTING SYSTEM")
    print("=" * 60)
    
    # Test alert
    print("\nTesting alert system...")
    alert_on_error("TEST_ALERT", "This is a test alert from the Empire AI system.", send_email=False)
    
    # Check for spikes
    print("\nChecking for error spikes...")
    check_for_spikes()
    
    print("\n" + "=" * 60)
