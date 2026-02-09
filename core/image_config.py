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
            "python-dateutil"
        )
#        .run_commands("playwright install --with-deps chromium")
        .add_local_dir("utils", remote_path="/root/utils")
        .add_local_dir("workers", remote_path="/root/workers")
        .add_local_file("workers/instant_response.py", remote_path="/root/workers/instant_response.py")
        .add_local_dir("core", remote_path="/root/core")
        .add_local_dir("api", remote_path="/root/api")
        # Selective module mounting to avoid 70k+ legacy files
        .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
        .add_local_dir("modules/database", remote_path="/root/modules/database")
        .add_local_dir("modules/ai", remote_path="/root/modules/ai")
        .add_local_dir("modules/analytics", remote_path="/root/modules/analytics")
        .add_local_dir("modules/vapi", remote_path="/root/modules/vapi")
        .add_local_dir("modules/learning", remote_path="/root/modules/learning")
        .add_local_dir("modules/bridge", remote_path="/root/modules/bridge")
        .add_local_file("modules/outbound_dialer.py", remote_path="/root/modules/outbound_dialer.py")
    )

image = get_base_image()
# Portal image will add 'public' mount
portal_image = get_base_image().add_local_dir("public", remote_path="/root/public")

# Consolidated secret vault - NOW USING THE SOVEREIGN VAULT
# This ensures we pull verified keys programmatically sealed in Sprint 1.
VAULT = modal.Secret.from_name("sovereign-vault")
