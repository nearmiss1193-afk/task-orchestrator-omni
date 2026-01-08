"""
EMPIRE AUTOMATION HUB (Modal Cron Jobs)
=======================================
Scheduled automation for:
- Email Poller (every 15 min)
- Cloud Inspector (every hour)
- Auto-Responder (every 30 min)
"""
import modal
import os

app = modal.App("empire-automation-hub")

# Image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv",
    "supabase",
    "fastapi",
    "google-auth",
    "google-auth-oauthlib", 
    "google-api-python-client"
)\
.add_local_file("email_poller.py", remote_path="/root/email_poller.py")\
.add_local_file("cloud_inspector.py", remote_path="/root/cloud_inspector.py")\
.add_local_file("auto_responder.py", remote_path="/root/auto_responder.py")\
.add_local_file("gmail_credentials.json", remote_path="/root/gmail_credentials.json")\
.add_local_file("gmail_token.json", remote_path="/root/gmail_token.json")\
.add_local_dir("modules", remote_path="/root/modules", ignore=["ghl-mcp", "descript-mcp", "node_modules", "__pycache__", "**/*.zip", "**/*.db"])


# ============ EMAIL POLLER (Every 15 minutes) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    schedule=modal.Cron("*/15 * * * *")  # Every 15 minutes
)
def email_poller_cron():
    """Check inbox for new leads every 15 minutes."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from email_poller import poll_inbox
    poll_inbox()


# ============ CLOUD INSPECTOR (Every hour) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    schedule=modal.Cron("0 * * * *")  # Every hour on the hour
)
def cloud_inspector_cron():
    """Run system health patrol every hour."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from cloud_inspector import run_patrol
    run_patrol()


# ============ AUTO-RESPONDER (Every 30 minutes) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    schedule=modal.Cron("*/30 * * * *")  # Every 30 minutes
)
def auto_responder_cron():
    """Process emails and send auto-responses every 30 minutes."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from auto_responder import process_and_respond
    # Run in LIVE mode (not dry run) for production
    process_and_respond(dry_run=False)


# ============ HEALTH CHECK ============
@app.function(image=image)
@modal.web_endpoint(method="GET", label="automation-health")
def automation_health():
    from datetime import datetime
    return {
        "status": "ONLINE",
        "service": "Empire Automation Hub",
        "cron_jobs": [
            {"name": "email_poller", "schedule": "*/15 * * * *"},
            {"name": "cloud_inspector", "schedule": "0 * * * *"},
            {"name": "auto_responder", "schedule": "*/30 * * * *"}
        ],
        "timestamp": datetime.now().isoformat()
    }


# ============ LOCAL ENTRYPOINT ============
@app.local_entrypoint()
def main():
    print("🤖 Empire Automation Hub")
    print("=" * 40)
    print("CRON JOBS:")
    print("  - Email Poller: Every 15 minutes")
    print("  - Cloud Inspector: Every hour")
    print("  - Auto-Responder: Every 30 minutes")
    print("")
    print("Deploy with: modal deploy modal_automation_hub.py")
