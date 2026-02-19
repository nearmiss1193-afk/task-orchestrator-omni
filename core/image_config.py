"""
MISSION: CORE IMAGE & SECRET CONFIGURATION
Shared infrastructure for all Modal workers
"""
import os
import modal
from dotenv import load_dotenv

load_dotenv()

# app = modal.App("nexus-outreach-v1") # Removed to allow multi-app separation

def get_base_image():
    return (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("git")
        .pip_install(
            "playwright",
            "python-dotenv",
            "requests",
            "supabase",
            "fastapi",
            "stripe",
            "resend",
            "google-generativeai>=0.5.0",
            "dnspython",
            "pytz",
            "python-dateutil",
            "psycopg2-binary",
            "Social-Post-API",
            "beautifulsoup4"
        )
#        .run_commands("playwright install --with-deps chromium")
        .add_local_dir("utils", remote_path="/root/utils")
        .add_local_dir("workers", remote_path="/root/workers")
        .add_local_file("workers/instant_response.py", remote_path="/root/workers/instant_response.py")
        .add_local_dir("core", remote_path="/root/core")
        .add_local_dir("api", remote_path="/root/api")
        .add_local_dir("scripts", remote_path="/root/scripts")
        .add_local_dir("handlers", remote_path="/root/handlers")
        # Selective module mounting to avoid 70k+ legacy files
        .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
        .add_local_dir("modules/database", remote_path="/root/modules/database")
        .add_local_dir("modules/ai", remote_path="/root/modules/ai")
        .add_local_dir("modules/analytics", remote_path="/root/modules/analytics")
        .add_local_dir("modules/vapi", remote_path="/root/modules/vapi")
        .add_local_dir("modules/learning", remote_path="/root/modules/learning")
        .add_local_dir("modules/bridge", remote_path="/root/modules/bridge")
        .add_local_dir("modules/handlers", remote_path="/root/modules/handlers")
        .add_local_dir("modules/dispatch", remote_path="/root/modules/dispatch")
        .add_local_file("modules/outbound_dialer.py", remote_path="/root/modules/outbound_dialer.py")
        .add_local_file("modules/autonomous_inspector.py", remote_path="/root/modules/autonomous_inspector.py")
    )

image = get_base_image()
# Portal image will add 'public' mount
portal_image = get_base_image().add_local_dir("public", remote_path="/root/public")

# Consolidated secret vault - NOW USING THE SOVEREIGN VAULT VIA FROM_DICT
# This ensures we pull verified keys programmatically sealed in Sprint 1.
VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "DATABASE_URL": "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres",
    "AYRSHARE_API_KEY": "57FCF9E6-1B534A66-9F05E51C-9ADE2CA5",
    "RESEND_API_KEY": "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy",
    "RESEND_FROM_EMAIL": "Dan <owner@aiserviceco.com>",
    "GROK_API_KEY": "xai-w1v5Y6E8F7G9H0J1K2L3M4N5P6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4J5K6L7M8N9P0Q1R2S3T4U5V6W7X8Y9Z0",
    "XAI_API_KEY": "xai-w1v5Y6E8F7G9H0J1K2L3M4N5P6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4J5K6L7M8N9P0Q1R2S3T4U5V6W7X8Y9Z0",
    "GHL_SMS_WEBHOOK_URL": "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd",
    "STRIPE_SECRET_KEY": "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",
})
