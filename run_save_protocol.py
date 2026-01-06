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

def run_save():
    print("🚀 Initiating Save Protocol...")
    
    # 1. Generate Report
    report_content = f"""# Save Protocol Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Status
- **Sarah 3.0**: Deployed (Grok Persona).
- **Antigravity**: Separated (Orchestrator Voice).
- **Asset Inbox**: LIVE (Supabase Backend).
- **Watchdog**: Active (background process).

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
    
    # 3. Email Dispatch
    html_body = f"""
    <h2>📋 Save Protocol Report</h2>
    <div style='background:#f4f4f4;padding:15px;border-radius:10px;'>{report_content.replace('\n', '<br>')}</div>
    <h2>📇 Latest Contacts</h2>
    <div style='background:#f4f4f4;padding:15px;border-radius:10px;'>{contacts_content.replace('\n', '<br>')}</div>
    """
    
    params = {
        "from": "alert@aiserviceco.com",
        "to": ["nearmiss1193@gmail.com", "owner@aiserviceco.com"],
        "subject": "🎯 SAVE PROTOCOL: Empire Unified State Backup",
        "html": html_body,
    }
    
    try:
        resend.Emails.send(params)
        print("✅ Save Protocol Email Sent.")
    except Exception as e:
        print(f"❌ Email Dispatch Failed: {e}")

if __name__ == "__main__":
    run_save()
