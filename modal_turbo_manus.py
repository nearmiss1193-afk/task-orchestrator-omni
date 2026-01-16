import modal
import os

# Define the image with necessary dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("requests", "psycopg2-binary", "python-dotenv")
    .add_local_dir(".", remote_path="/root", ignore=[
        "**/node_modules", 
        "**/.next", 
        "**/dist",
        "**/.git",
        "**/.ghl_browser_data",
        "**/backups",
        "**/*_b64.txt",
        "**/*.log",
        "**/__pycache__",
        "**/*.mp4",
        "**/*.mov",
        "**/tmp",
        "output/**",
        "sovereign_digests/**",
        "apps/**"
    ])
)

app = modal.App("turbo-manus-campaign")

# Define secrets from environment
VAULT = modal.Secret.from_dict({
    "DB_HOST": os.environ.get("DB_HOST", "db.rzcpfwkygdvoshtwxncs.supabase.co"),
    "DB_NAME": os.environ.get("DB_NAME", "postgres"),
    "DB_USER": os.environ.get("DB_USER", "postgres"),
    "DB_PASS": os.environ.get("DB_PASS", "Inez11752990@"),
    "VAPI_KEY": os.environ.get("VAPI_KEY"),
    "NEXT_PUBLIC_SUPABASE_URL": os.environ.get("NEXT_PUBLIC_SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "GHL_SMS_WEBHOOK": "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd",
    "GHL_EMAIL_WEBHOOK": "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/cf2e8a9c-e943-4d78-9f6f-cd66bb9a2e42"
})

@app.function(
    image=image,
    secrets=[VAULT],
    schedule=modal.Cron("*/10 * * * *"), # Every 10 minutes
    timeout=600 # 10 minutes max
)
def run_manus_cycle():
    """Execute one cycle of the turbo manus campaign"""
    import sys
    import os
    
    # Change into the root directory where files were added
    os.chdir("/root")
    sys.path.append("/root")
    
    from turbo_manus import run_campaign_cycle
    
    print("🚀 [MODAL] Starting Turbo Manus Cycle...")
    try:
        results = run_campaign_cycle()
        print(f"✅ [MODAL] Cycle Complete: {results}")
        return results
    except Exception as e:
        print(f"❌ [MODAL] Cycle Failed: {e}")
        import traceback
        traceback.print_exc()
        raise e

@app.local_entrypoint()
def main():
    run_manus_cycle.remote()
