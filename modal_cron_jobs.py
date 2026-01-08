"""
EMPIRE CRON JOBS (Simplified)
============================
Scheduled automation - CRON ONLY (no web endpoints).
"""
import modal
import os

app = modal.App("empire-cron-jobs")

# Image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv",
    "supabase",
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
    schedule=modal.Cron("*/15 * * * *")
)
def email_poller_job():
    """Check inbox for new leads every 15 minutes."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from email_poller import poll_inbox
    print("📬 Email Poller Running...")
    poll_inbox()


# ============ CLOUD INSPECTOR (Every hour) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    schedule=modal.Cron("0 * * * *")
)
def cloud_inspector_job():
    """Run system health patrol every hour."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from cloud_inspector import run_patrol
    print("🔍 Cloud Inspector Running...")
    run_patrol()


# ============ AUTO-RESPONDER (Every 30 minutes) ============
@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(path=os.path.join(os.getcwd(), ".env"))],
    schedule=modal.Cron("*/30 * * * *")
)
def auto_responder_job():
    """Process emails and send auto-responses every 30 minutes."""
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    
    from auto_responder import process_and_respond
    print("🤖 Auto-Responder Running...")
    process_and_respond(dry_run=False)


# ============ LOCAL ENTRYPOINT ============
@app.local_entrypoint()
def main():
    print("🤖 Empire Cron Jobs")
    print("=" * 40)
    print("SCHEDULED:")
    print("  - Email Poller: Every 15 minutes")
    print("  - Cloud Inspector: Every hour")
    print("  - Auto-Responder: Every 30 minutes")
    print("")
    print("Deploy: modal deploy modal_cron_jobs.py")
