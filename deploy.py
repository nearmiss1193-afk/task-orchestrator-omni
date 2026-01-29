import sys
import os
import modal
from core.apps import engine_app as app

# IMAGE CONFIGURATION
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
            "google-generativeai>=0.5.0",
            "dnspython",
            "pytz",
            "python-dateutil",
            "psycopg2-binary"
        )
        .run_commands("playwright install --with-deps chromium")
        .add_local_dir("utils", remote_path="/root/utils")
        .add_local_dir("workers", remote_path="/root/workers")
        .add_local_dir("core", remote_path="/root/core")
        .add_local_dir("api", remote_path="/root/api")
        .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
        .add_local_dir("modules/database", remote_path="/root/modules/database")
        .add_local_dir("modules/ai", remote_path="/root/modules/ai")
        .add_local_dir("modules/analytics", remote_path="/root/modules/analytics")
        .add_local_file("modules/outbound_dialer.py", remote_path="/root/modules/outbound_dialer.py")
    )

image = get_base_image()
VAULT = modal.Secret.from_name("sovereign-vault")

# Diagnostic function 1: Environment Verify
@app.function(image=image, secrets=[VAULT])
def print_env_diagnostics():
    """Print cloud environment vars for verification"""
    import os
    print(f"🔗 CLOUD SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
    key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    if key:
        print(f"🔑 CLOUD SUPABASE_KEY: {key[:10]}...{key[-5:]}")
    else:
        print("🔑 CLOUD SUPABASE_KEY: MISSING")
    print(f"📞 CLOUD GHL_LOCATION_ID: {os.environ.get('GHL_LOCATION_ID')}")
    print(f"🔗 CLOUD GHL_SMS_WEBHOOK_URL: {os.environ.get('GHL_SMS_WEBHOOK_URL')}")
    print(f"🔗 CLOUD GHL_EMAIL_WEBHOOK_URL: {os.environ.get('GHL_EMAIL_WEBHOOK_URL')}")

# Diagnostic function 2: DB Verify
@app.function(image=image, secrets=[VAULT])
def test_db_connection():
    """Quick DB connectivity test"""
    from modules.database.supabase_client import get_supabase
    try:
        sb = get_supabase()
        res = sb.table("contacts_master").select("*", count="exact").execute()
        count = res.count
        print(f"✅ DB CONNECTED: Total Leads in Cloud: {count}")
        if res.data:
            print(f" - Sample Cloud Lead: {res.data[0]['id']} ({res.data[0].get('full_name')})")
            print(f"✅ DB CONNECTED: Lead ID found: {res.data[0]['id']}")
        else:
            print("⚠️ DB CONNECTED but no leads found.")
        return True
    except Exception as e:
        print(f"❌ DB TEST FAIL: {e}")
        raise

# Diagnostic function 3: Outreach Verify
@app.function(image=image, secrets=[VAULT])
def verify_outreach_worker():
    """Live verification of the outreach worker logic (Rule #1)"""
    from workers.outreach import dispatch_sms_logic
    print("🚀 Triggering live worker verification (Phase A)...")
    # DEFINITIVE CLOUD LEAD ID
    test_lead_id = "c086f2ce-72f5-4f9f-b414-e0432908c6bc"
    try:
        res = dispatch_sms_logic.local(lead_id=test_lead_id, message="Antigravity Phase A: Bridge Operational.")
        print(f"✅ Worker result: {res}")
        return True
    except Exception as e:
        print(f"⚠️ Worker test: {e}")
        return True

@app.function(image=image, secrets=[VAULT])
def test_db_psycopg2():
    """Diagnostic bypass of Supabase SDK using raw psycopg2"""
    import os
    import psycopg2
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL missing in Vault")
        return
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT id, full_name FROM contacts_master LIMIT 5;")
        leads = cur.fetchall()
        print(f"✅ RAW PSQL CONNECTED: Found {len(leads)} leads.")
        for lead in leads:
            print(f" - {lead[1]} ({lead[0]})")
        conn.close()
    except Exception as e:
        print(f"❌ RAW PSQL FAIL: {e}")

if __name__ == "__main__":
    print("Nexus Outreach V1 - Clean Architecture")
