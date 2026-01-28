"""
MISSION: CORE IMAGE & SECRET CONFIGURATION
Shared infrastructure for all Modal workers
"""
import os
import modal
from dotenv import load_dotenv

load_dotenv()

app = modal.App("nexus-outreach-v1")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "playwright",
        "python-dotenv",
        "requests",
        "supabase",
        "fastapi",
        "stripe",
        "google-generativeai>=0.5.0",
        "dnspython",
        "pytz"
    )
    .run_commands("playwright install --with-deps chromium")
    .add_local_file("sovereign_config.json", remote_path="/root/sovereign_config.json")
    .add_local_dir("modules", remote_path="/root/modules")
   .add_local_dir("public", remote_path="/root/public")
    .add_local_dir("utils", remote_path="/root/utils")
    .add_local_dir("workers", remote_path="/root/workers")
    .add_local_dir("core", remote_path="/root/core")
    .add_local_dir("api", remote_path="/root/api")
)

# Consolidated secret vault (removed duplicates per Grok audit)
VAULT = modal.Secret.from_dict({
    "NEXT_PUBLIC_SUPABASE_URL": str(os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""),
    "SUPABASE_URL": str(os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""),
    "SUPABASE_SERVICE_ROLE_KEY": str(os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""),
    "GEMINI_API_KEY": str(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""),
    "GHL_API_TOKEN": str(os.environ.get("GHL_API_TOKEN") or ""),
    "GHL_LOCATION_ID": str(os.environ.get("GHL_LOCATION_ID") or ""),
    "GHL_EMAIL": str(os.environ.get("GHL_EMAIL") or ""),
    "GHL_PASSWORD": str(os.environ.get("GHL_PASSWORD") or ""),
    "VAPI_PRIVATE_KEY": str(os.environ.get("VAPI_PRIVATE_KEY") or ""),
    "STRIPE_SECRET_KEY": str(os.environ.get("STRIPE_SECRET_KEY") or ""),
    "APOLLO_API_KEY": str(os.environ.get("APOLLO_API_KEY") or ""),
    "GHL_SMS_WEBHOOK_URL": str(os.environ.get("GHL_SMS_WEBHOOK_URL") or ""),
    "GHL_EMAIL_WEBHOOK_URL": str(os.environ.get("GHL_EMAIL_WEBHOOK_URL") or "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"),
})
