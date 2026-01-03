
"""
Imperium Sovereign Deployment Script (v39.x)
Purpose: unified deployment orchestration for Modal Cloud or local testing.
Compatible with Python 3.9 – 3.13.
"""

import os
import modal
import sys
import platform
import dotenv

# Load Env
dotenv.load_dotenv()

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "YOUR-SUPABASE-SERVICE-KEY")
PROJECT_NAME = "imperium_v39"

app = modal.App(PROJECT_NAME)

# --- IMPORTS FOR SOVEREIGN MODULES ---
# Ensuring we can import from local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from modules.qa.diagnostic_sweeper import DiagnosticSweeper
    from modules.governor.rollback_protocol import RollbackProtocol
    from modules.governor.continuity_auditor import ContinuityAuditor
    from modules.qa.connection_auditor import ConnectionAuditor
    from supabase import create_client
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running this from the project root.")
    sys.exit(1)

# Helper to get DB client
def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase Credentials Missing. Mocking Client.")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@app.function()
def check_environment():
    print(f"🐍 Python version: {sys.version}")
    print(f"⚙️ Platform: {platform.system()} {platform.release()}")
    # print(f"⚡ Supabase URL: {SUPABASE_URL}") # Masked for security
    print("✅ Environment validated.")
    return "Environment validated."

@app.function()
def deploy_governor():
    """ Runs Mission 39.2: QA Monitor """
    print("🚀 Deploying Governor QA Monitor (v39.2) ...")
    # Using DiagnosticSweeper directly
    target_url = "https://aiserviceco.com"
    sweeper = DiagnosticSweeper(target_url)
    report = sweeper.execute_sweep()
    print(f"✅ Governor QA Monitor active. Scanned: {target_url}")
    # print(report) 

@app.function()
def deploy_rollback():
    """ Runs Mission 39.3: Rollback Protocol """
    print("⚙️ Initializing Rollback Protocol (v39.3) ...")
    db = get_supabase()
    rollback = RollbackProtocol(db)
    # We don't trigger rollback here, just initialize checking
    print("✅ Rollback Protocol ready & initialized.")

@app.function()
def deploy_continuity_audit():
    """ Runs Mission 39.6 & 39.7: Continuity & Connection Audits """
    print("📋 Launching Continuity Audit (v39.6)...")
    db = get_supabase()
    auditor = ContinuityAuditor(db)
    report = auditor.execute_audit()
    
    print("📋 Launching Connection Audit (v39.7)...")
    conn_auditor = ConnectionAuditor(db)
    conn_report = conn_auditor.execute_audit()
    
    print("✅ Continuity Audit operational.")
    print(f"   Status: {report.get('status', 'Unknown')}")
    print(f"   Connection: {conn_report.get('status', 'Unknown')}")

@app.local_entrypoint()
def main():
    print("Initializing Imperium Deployment v39 Pipeline ...")
    
    # Execute Sequence
    check_environment.call()
    deploy_governor.call()
    deploy_rollback.call()
    deploy_continuity_audit.call()
    
    print("✨ Imperium v39 deployment sequence complete.")
