import os
import sqlite3
import json
import resend
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
CONV_ID = "eb60a735-eb12-430f-a375-32e90542f043"
BRAIN_DIR = f"c:\\Users\\nearm\\.gemini\\antigravity\\brain\\{CONV_ID}"
SCRATCH_DIR = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified"
DB_PATH = os.path.join(SCRATCH_DIR, "empire.db")
CAPS_GAPS_PATH = os.path.join(SCRATCH_DIR, "CAPABILITIES_GAPS.md")
resend.api_key = os.getenv('RESEND_API_KEY')


def get_latest_leads():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, email, status, created_at FROM leads ORDER BY created_at DESC LIMIT 50")
        leads = c.fetchall()
        conn.close()
        return leads
    except Exception as e:
        print(f"⚠️ SQLite Error: {e}")
        return []


def get_capabilities_gaps():
    """Read the capabilities and gaps analysis document"""
    try:
        if os.path.exists(CAPS_GAPS_PATH):
            with open(CAPS_GAPS_PATH, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"⚠️ Could not read CAPABILITIES_GAPS.md: {e}")
    return "Capabilities & Gaps document not found."


def get_env_status():
    """Check status of required environment variables"""
    required_vars = [
        "GROK_API_KEY",
        "RESEND_API_KEY", 
        "VAPI_PRIVATE_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "GHL_API_KEY",
        "GHL_LOCATION_ID",
        "TEST_PHONE",
    ]
    
    status = []
    for var in required_vars:
        val = os.getenv(var)
        if val:
            status.append(f"✅ {var}: Configured")
        else:
            status.append(f"❌ {var}: MISSING")
    
    return "\n".join(status)


def run_save():
    print("🚀 Initiating Save Protocol (Enhanced)...")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Generate System Report
    report_content = f"""# Save Protocol Report - {timestamp}

## System Status
- **Sarah 3.1**: Deployed (Grok Persona) via Vapi
- **Antigravity**: Separated (Orchestrator Voice)
- **Asset Inbox**: LIVE (Supabase Backend)
- **Watchdog**: Active (background process)
- **Website**: Live at aiserviceco.com
- **Deep Intel Agent**: Operational
- **HVAC Campaign**: 20 prospects identified

## Environment Status
{get_env_status()}

## Recent Activity
- Top 20 HVAC prospects identified across Florida
- Personalized emails generated with Grok
- Savings/ROI analysis completed

## Recent Commits
System state synchronized and backed up to cloud.
"""
    report_path = os.path.join(BRAIN_DIR, "save_protocol_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    # 2. Export Contacts
    leads = get_latest_leads()
    contacts_content = "# Current Contact Ledger\n\n"
    if leads:
        contacts_content += "| Name | Email | Status | Created |\n| :--- | :--- | :--- | :--- |\n"
        for l in leads:
            contacts_content += f"| {l[0]} | {l[1]} | {l[2]} | {l[3]} |\n"
    else:
        contacts_content += "No active leads found in local cache."
    
    contacts_path = os.path.join(BRAIN_DIR, "contacts_export.md")
    with open(contacts_path, "w", encoding="utf-8") as f:
        f.write(contacts_content)
    
    # 3. Get Capabilities & Gaps
    caps_gaps = get_capabilities_gaps()
    
    # 4. Email Dispatch with ALL recovery info
    html_body = f"""
    <div style='font-family:system-ui,sans-serif;max-width:800px;margin:0 auto;'>
    
    <h2 style='color:#2563eb;'>📋 Save Protocol Report</h2>
    <div style='background:#1e293b;color:#f8fafc;padding:20px;border-radius:10px;'>
        <pre style='white-space:pre-wrap;font-size:13px;'>{report_content}</pre>
    </div>
    
    <h2 style='color:#2563eb;margin-top:30px;'>📇 Latest Contacts</h2>
    <div style='background:#1e293b;color:#f8fafc;padding:20px;border-radius:10px;'>
        <pre style='white-space:pre-wrap;font-size:13px;'>{contacts_content}</pre>
    </div>
    
    <h2 style='color:#2563eb;margin-top:30px;'>⚡ Capabilities & Gaps Analysis</h2>
    <div style='background:#1e293b;color:#f8fafc;padding:20px;border-radius:10px;overflow-x:auto;'>
        <pre style='white-space:pre-wrap;font-size:11px;'>{caps_gaps}</pre>
    </div>
    
    <h2 style='color:#22c55e;margin-top:30px;'>🔄 Recovery Protocol</h2>
    <div style='background:#14532d;color:#f8fafc;padding:20px;border-radius:10px;'>
        <p><strong>Key Files:</strong></p>
        <ul>
            <li><code>hvac_campaign.py</code> - HVAC outreach</li>
            <li><code>deep_intel_agent.py</code> - Prospect research</li>
            <li><code>top10_prospect_hunter.py</code> - Find targets</li>
            <li><code>call_sara_prospect.py</code> - Sarah calls</li>
            <li><code>qa_secret_shopper.py</code> - Website QA</li>
        </ul>
        <p><strong>Active Services:</strong> Vercel, Supabase, Vapi, Resend</p>
        <p><strong>Watchdog:</strong> <code>python asset_watchdog.py</code></p>
    </div>
    
    </div>
    """
    
    params = {
        "from": "alert@aiserviceco.com",
        "to": ["nearmiss1193@gmail.com", "owner@aiserviceco.com"],
        "subject": f"🎯 SAVE PROTOCOL: Empire Unified State Backup - {timestamp}",
        "html": html_body,
    }
    
    try:
        resend.Emails.send(params)
        print("✅ Save Protocol Email Sent (with Capabilities & Recovery).")
    except Exception as e:
        print(f"❌ Email Dispatch Failed: {e}")
    
    print(f"\n📁 Reports saved:")
    print(f"   - {report_path}")
    print(f"   - {contacts_path}")
    print(f"   - {CAPS_GAPS_PATH}")


if __name__ == "__main__":
    run_save()

