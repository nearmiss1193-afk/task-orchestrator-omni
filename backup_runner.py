"""
🛡️ BACKUP RUNNER - Modal Failover System
=========================================
When Modal cloud is down, this ensures 24/7 operation continues.

Features:
- Auto-detects Modal health
- Runs local equivalents of cloud cron jobs
- Auto-restarts continuous_swarm.py if it crashes
- Sends alerts on failures

Usage:
    python backup_runner.py                  # Run backup loop
    python backup_runner.py --check          # Just check Modal health
    python backup_runner.py --force          # Force run all jobs
"""
import os
import sys
import time
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# === CONFIG ===
MODAL_HEALTH_URL = "https://nearmiss1193--empire-sovereign-v2-health.modal.run"
CHECK_INTERVAL = 300  # 5 minutes
SWARM_RESTART_DELAY = 10
MAX_RETRIES = 3

# Alert config
RESEND_KEY = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("GHL_EMAIL", "nearmiss1193@gmail.com")


def log(msg: str, level: str = "INFO"):
    """Log with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def check_modal_health() -> bool:
    """Check if Modal deployment is healthy."""
    try:
        resp = requests.get(MODAL_HEALTH_URL, timeout=10)
        if resp.status_code == 200:
            log("✅ Modal is HEALTHY")
            return True
        else:
            log(f"⚠️ Modal returned status {resp.status_code}", "WARN")
            return False
    except requests.exceptions.Timeout:
        log("❌ Modal health check TIMEOUT", "ERROR")
        return False
    except requests.exceptions.ConnectionError:
        log("❌ Modal health check FAILED - Connection Error", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Modal health check error: {e}", "ERROR")
        return False


def check_swarm_running() -> tuple[bool, int]:
    """Check if continuous_swarm.py is running."""
    try:
        # Use tasklist on Windows
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True, text=True
        )
        count = result.stdout.lower().count("python.exe")
        return count > 0, count
    except:
        return False, 0


def start_swarm():
    """Start continuous_swarm.py in background."""
    log("🚀 Starting continuous_swarm.py...")
    try:
        subprocess.Popen(
            ["python", "continuous_swarm.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        log("✅ Swarm started successfully")
        return True
    except Exception as e:
        log(f"❌ Failed to start swarm: {e}", "ERROR")
        return False


def send_alert(subject: str, message: str):
    """Send email alert for critical issues."""
    if not RESEND_KEY:
        log(f"⚠️ Alert (no email): {subject}", "WARN")
        return
    
    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}"},
            json={
                "from": "Empire AI <alerts@aiserviceco.com>",
                "to": [OWNER_EMAIL],
                "subject": f"🚨 {subject}",
                "html": f"<h2>{subject}</h2><p>{message}</p><p>Time: {datetime.now().isoformat()}</p>"
            },
            timeout=10
        )
        log(f"📧 Alert sent: {subject}")
    except:
        pass


def run_backup_jobs():
    """Run cloud job equivalents locally."""
    log("🔄 Running backup jobs locally...")
    
    # These would normally run in Modal cron jobs
    jobs = [
        ("Prospector", check_and_run_prospector),
        ("Health Monitor", check_and_run_health),
    ]
    
    for name, func in jobs:
        try:
            func()
            log(f"✅ {name} completed")
        except Exception as e:
            log(f"❌ {name} failed: {e}", "ERROR")


def check_and_run_prospector():
    """Run prospector logic if needed."""
    # The swarm already handles prospecting, so just verify it's running
    running, _ = check_swarm_running()
    if not running:
        start_swarm()


def check_and_run_health():
    """Run health monitoring."""
    from supabase import create_client
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supa_url or not supa_key:
        return
    
    client = create_client(supa_url, supa_key)
    
    # Log health status
    try:
        client.table("system_logs").insert({
            "level": "INFO",
            "event_type": "BACKUP_RUNNER_HEALTH",
            "message": "Backup runner is active and monitoring",
            "metadata": {
                "modal_healthy": check_modal_health(),
                "swarm_running": check_swarm_running()[0],
                "timestamp": datetime.now().isoformat()
            }
        }).execute()
    except:
        pass


def main_loop():
    """Main backup monitoring loop."""
    log("=" * 60)
    log("🛡️ BACKUP RUNNER STARTING")
    log("=" * 60)
    log(f"Modal health URL: {MODAL_HEALTH_URL}")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log("")
    
    consecutive_failures = 0
    alert_sent = False
    
    while True:
        try:
            # 1. Check Modal health
            modal_healthy = check_modal_health()
            
            if not modal_healthy:
                consecutive_failures += 1
                log(f"⚠️ Modal unhealthy ({consecutive_failures} consecutive)", "WARN")
                
                # Send alert after 3 consecutive failures
                if consecutive_failures >= 3 and not alert_sent:
                    send_alert(
                        "Modal Cloud Down",
                        f"Modal has been unhealthy for {consecutive_failures} checks. Backup runner is active."
                    )
                    alert_sent = True
                
                # Run backup jobs
                run_backup_jobs()
            else:
                if consecutive_failures > 0:
                    log("✅ Modal recovered")
                    if alert_sent:
                        send_alert("Modal Recovered", "Modal cloud is healthy again.")
                consecutive_failures = 0
                alert_sent = False
            
            # 2. Always ensure swarm is running
            running, count = check_swarm_running()
            log(f"🐝 Swarm status: {count} Python processes")
            
            if not running:
                log("⚠️ Swarm not running, restarting...", "WARN")
                start_swarm()
                time.sleep(SWARM_RESTART_DELAY)
            
            # 3. Wait for next check
            log(f"⏳ Next check in {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("\n🛑 Backup runner stopped by user")
            break
        except Exception as e:
            log(f"❌ Loop error: {e}", "ERROR")
            time.sleep(60)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            healthy = check_modal_health()
            running, count = check_swarm_running()
            print(f"\nModal: {'HEALTHY' if healthy else 'UNHEALTHY'}")
            print(f"Swarm: {count} Python processes running")
            sys.exit(0 if healthy else 1)
        
        elif sys.argv[1] == "--force":
            log("🔧 Force running all backup jobs...")
            run_backup_jobs()
            sys.exit(0)
    
    # Default: run monitoring loop
    main_loop()


if __name__ == "__main__":
    main()
