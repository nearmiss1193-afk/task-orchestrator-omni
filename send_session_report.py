"""Send campaign report email to owner."""
import os
import resend
from datetime import datetime

# Load .env
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"').strip("'")
except Exception: pass

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("❌ RESEND_API_KEY not found")
    exit(1)

resend.api_key = RESEND_API_KEY

# Today's report
report_html = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a2e; color: #fff; padding: 20px; border-radius: 10px;">
    <h1 style="color: #00d4ff;">📊 Session Report - 2026-01-10</h1>
    
    <h2 style="color: #00ff88;">✅ Completed Today</h2>
    <ul>
        <li>Fixed Vapi daily limit → Twilio number (UNLIMITED)</li>
        <li>Fixed Sarah's script from inbound to outbound</li>
        <li>Upgraded Sarah to Rachel voice + Eleven Turbo v2.5</li>
        <li>Fixed Supabase schema issue (email column)</li>
        <li>HVAC Florida campaign: <strong>5/5 SUCCESSFUL</strong></li>
    </ul>
    
    <h2 style="color: #ffaa00;">📞 Calls Made</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: #2a2a4e;">
            <th style="padding: 8px; text-align: left; border: 1px solid #444;">Company</th>
            <th style="padding: 8px; text-align: left; border: 1px solid #444;">Status</th>
        </tr>
        <tr><td style="padding: 8px; border: 1px solid #444;">All American Air & Electric</td><td style="padding: 8px; border: 1px solid #444;">✅ Called</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #444;">B & B Air Conditioning Inc.</td><td style="padding: 8px; border: 1px solid #444;">✅ Called</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #444;">Coast to Coast Heating & Air</td><td style="padding: 8px; border: 1px solid #444;">✅ Called</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #444;">Dial Duron Service Co.</td><td style="padding: 8px; border: 1px solid #444;">✅ Called</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #444;">Desouzza's Heating & Air</td><td style="padding: 8px; border: 1px solid #444;">✅ Called</td></tr>
    </table>
    
    <h2 style="color: #00d4ff;">🔗 Quick Links</h2>
    <p><a href="https://www.aiserviceco.com/dashboard.html" style="color: #00ff88; font-size: 18px;">📊 Dashboard</a></p>
    <p><a href="https://app.gohighlevel.com" style="color: #00d4ff;">GHL Portal</a> | <a href="https://dashboard.vapi.ai" style="color: #00d4ff;">Vapi Dashboard</a></p>
    
    <hr style="border-color: #444; margin: 20px 0;">
    <p style="color: #888; font-size: 12px;">Empire Unified System • Autonomous Operations</p>
</div>
"""

params = {
    "from": "alert@aiserviceco.com",
    "to": ["owner@aiserviceco.com", "nearmiss1193@gmail.com"],
    "subject": f"📊 Empire Campaign Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "html": report_html
}

try:
    email = resend.Emails.send(params)
    print(f"✅ Email Sent! ID: {email.get('id')}")
    print(f"   To: owner@aiserviceco.com, nearmiss1193@gmail.com")
except Exception as e:
    print(f"❌ Email Failed: {e}")
