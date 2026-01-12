"""
TURBO STATUS REPORT - Send comprehensive system status email
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

RESEND_KEY = os.getenv("RESEND_API_KEY")

def send_status_report():
    """Send status report to owner"""
    now = datetime.now()
    
    report_html = f"""
    <h2>🚀 Empire Autonomous System - Status Report</h2>
    <p><strong>Time:</strong> {now.strftime('%Y-%m-%d %I:%M %p ET')}</p>
    
    <h3>✅ CRITICAL ACCOMPLISHMENTS TODAY</h3>
    <ul>
        <li><strong>Modal Deployment FIXED</strong> - Reduced from 7 to 5 cron jobs (free tier limit)</li>
        <li><strong>AttributeError Bug FIXED</strong> - cloud_multi_touch now handles None safely</li>
        <li><strong>Sarah Inbound/Outbound FIXED</strong> - Dynamic greeting based on call direction</li>
        <li><strong>All Functions Verified Running</strong> - cloud_prospector + cloud_multi_touch succeeded</li>
    </ul>
    
    <h3>📊 ACTIVE SCHEDULES (5 of 5 Modal cron slots used)</h3>
    <ul>
        <li>self_healing_monitor - Every 15 minutes</li>
        <li>cloud_drip_campaign - Daily at 9 AM</li>
        <li>cloud_prospector - Every 2 hours</li>
        <li>cloud_multi_touch - Hourly 8 AM - 6 PM Mon-Sat</li>
        <li>sovereign_worker - Every 30 minutes</li>
    </ul>
    
    <h3>⏸️ DISABLED (can be re-enabled with Modal upgrade)</h3>
    <ul>
        <li>social_media_poster - Daily at 8 AM</li>
        <li>social_media_analytics - Daily at 10 PM</li>
    </ul>
    
    <h3>🔗 DASHBOARDS</h3>
    <ul>
        <li><a href="https://modal.com/apps/nearmiss1193-afk/main/deployed/empire-sovereign-v2">Modal Dashboard</a></li>
        <li><a href="https://dashboard.vapi.ai/phone-numbers">Vapi Phone Numbers</a></li>
        <li><a href="https://aiserviceco.com/sovereign.html">Empire Dashboard</a></li>
    </ul>
    
    <h3>📞 VAPI PHONE NUMBERS</h3>
    <ul>
        <li>+1 (863) 213-2505 - AI Service Co (Sarah)</li>
        <li>+1 (863) 692-8474 - Sarah Personal</li>
        <li>+1 (863) 692-8548 - John Roofing Line</li>
        <li>+1 (904) 512-9565 - Riley (ALF Specialist)</li>
    </ul>
    
    <p><em>System is now fully autonomous. Prospecting every 2 hours, outreach hourly during business hours.</em></p>
    """
    
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_KEY}"},
        json={
            "from": "Empire System <system@aiserviceco.com>",
            "to": ["owner@aiserviceco.com", "nearmiss1193@gmail.com"],
            "subject": f"🚀 Empire Status Report - {now.strftime('%Y-%m-%d %I:%M %p')}",
            "html": report_html
        }
    )
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ Status report SENT! ID: {data.get('id')}")
        return True
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SENDING STATUS REPORT")
    print("="*60)
    send_status_report()
