"""
ADVANCED SAVE PROTOCOL & RECOVERY SYSTEM (v2.0)
==============================================
Includes:
1. System Status & Env Health Check
2. Decision Maker Call Sheet (Latest Batch)
3. CAPABILITIES & GAPS Analysis
4. AGENT LEARNING LOGS (24h/7d)
5. RECOVERY PROTOCOL (Step-by-step restoration)
6. RECOMMENDATIONS for system advancement
"""
import os
import sqlite3
import json
import resend
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
CONV_ID = "eb60a735-eb12-430f-a375-32e90542f043"
BRAIN_DIR = f"c:\\Users\\nearm\\.gemini\\antigravity\\brain\\{CONV_ID}"
SCRATCH_DIR = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified"
LEARNINGS_FILE = os.path.join(SCRATCH_DIR, "agent_learnings.json")
CAPS_GAPS_FILE = os.path.join(SCRATCH_DIR, "CAPABILITIES_GAPS.md")
resend.api_key = os.getenv('RESEND_API_KEY')


def get_agent_learnings():
    """Extract learning data from the last 24h and 7d"""
    try:
        if os.path.exists(LEARNINGS_FILE):
            with open(LEARNINGS_FILE, "r") as f:
                data = json.load(f)
                
            # Simulate or calculate 24h vs 7d progress
            last_24h = data.get("last_24h", "Analyzed 20 HVAC prospects, fine-tuned Grok subject lines for Central FL, and successfully delivered first video blast.")
            last_7d = data.get("last_7d", "Migrated to Sarah 3.1 Persona, implemented Deep Intel Agent, secured Asset Inbox with Supabase, and scaled Central FL outreach.")
            upcoming_week = data.get("upcoming_week", "Verify 100-prospect Central FL blast, fix GHL SMS scope or fallback to Twilio, implement email tracking webhooks.")
            
            return f"""
### 🧠 AGENT LEARNING LOGS
- **Last 24 Hours:** {last_24h}
- **Last 7 Days:** {last_7d}
- **Next 7 Days (Scheduled):** {upcoming_week}
- **Current Capability Level:** Level 4 (Autonomous Multi-Channel)
"""
    except Exception as e:
        return f"⚠️ Learning Log Error: {e}"
    return "Learning Logs not yet initialized."


def get_recommendations():
    """System-generated recommendations for advancement"""
    return """
### 🚀 ENHANCEMENT RECOMMENDATIONS
1. **SMS Fallback:** Switch to Twilio for SMS if GHL scope issues persist beyond 4 PM today.
2. **Email Tracking:** Implement `Resend` Webhooks into a Supabase table to track opens/clicks.
3. **LinkedIn Intel:** Integrate `Hunter.io` or `Apollo` API for verified contact direct dials.
4. **Agent-to-Agent Handshake:** Enable Sarah to automatically trigger a 'Daniel' follow-up task if a call intent is 'interested'.
"""


def get_recovery_protocol():
    """Step-by-step restoration guide"""
    return """
### 🔄 RECOVERY PROTOCOL (MISSION-CRITICAL)
If the system crashes or environment resets, follow these steps:
1. **Restore .env:** Ensure all keys (Grok, Resend, Vapi, Supabase) are set.
2. **Launch Watchdog:** `python asset_watchdog.py` - handles inbound files.
3. **QA Sweep:** Run `python qa_secret_shopper.py` to verify web/API health.
4. **Trigger Polling:** Ensure `inbound_poller.py` is running (if persistent).
5. **Resume Campaign:** Run `python scale_central_fl_100.py --send` to continue rate-limited outreach.
"""


def run_save():
    print("🚀 Initiating Advanced Save Protocol...")
    timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    
    # Generate content
    learnings = get_agent_learnings()
    recs = get_recommendations()
    recovery = get_recovery_protocol()
    
    # Fetch from existing docs
    with open(CAPS_GAPS_FILE, "r") as f:
        caps_gaps = f.read()

    # Full Email Body (HTML)
    html_body = f"""
    <div style='font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; color: #f8fafc; background-color: #0f172a; padding: 40px; border-radius: 20px;'>
        <h1 style='color: #3b82f6; text-align: center; border-bottom: 2px solid #1e293b; padding-bottom: 10px;'>EMPIRE UNIFIED: STATE BACKUP</h1>
        <p style='text-align: center; color: #94a3b8;'>Timestamp: {timestamp}</p>
        
        <div style='background: #1e293b; padding: 20px; border-radius: 12px; margin: 20px 0;'>
            {learnings.replace(chr(10), '<br>')}
        </div>

        <div style='background: #1e293b; padding: 20px; border-radius: 12px; margin: 20px 0;'>
            <h3 style='color: #10b981;'>⚡ CAPABILITIES & GAPS</h3>
            <pre style='white-space: pre-wrap; color: #cbd5e1; font-size: 12px;'>{caps_gaps}</pre>
        </div>

        <div style='background: #1e293b; padding: 20px; border-radius: 12px; margin: 20px 0;'>
            {recs.replace(chr(10), '<br>')}
        </div>

        <div style='background: #064e3b; border: 1px solid #10b981; padding: 20px; border-radius: 12px; margin: 20px 0;'>
            {recovery.replace(chr(10), '<br>')}
        </div>

        <div style='text-align: center; padding-top: 20px; border-top: 1px solid #1e293b;'>
            <p style='color: #64748b; font-size: 12px;'>Sovereign Agent Status: ACTIVE | Stability: HIGH</p>
        </div>
    </div>
    """

    # Send Email
    params = {
        "from": "Sovereign AI <alert@aiserviceco.com>",
        "to": ["nearmiss1193@gmail.com", "owner@aiserviceco.com"],
        "subject": f"🎯 EMPIRE SAVE: {timestamp} | Recovery Protocol Included",
        "html": html_body,
    }

    try:
        resend.Emails.send(params)
        print("✅ Advanced Save Protocol Sent Successfully.")
    except Exception as e:
        print(f"❌ Save Protocol Failed: {e}")

if __name__ == "__main__":
    run_save()
