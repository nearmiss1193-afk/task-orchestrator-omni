import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# Use GHL_EMAIL as the recipient, default to a likely guess if missing, but preferably from env.
TO_EMAIL = os.getenv("GHL_EMAIL") or "nearmiss1193@gmail.com" 

def send_report():
    if not RESEND_API_KEY:
        print("❌ FATAL: RESEND_API_KEY missing.")
        return

    report_path = "campaign_report_latest.md"
    if not os.path.exists(report_path):
        print(f"❌ Report file not found: {report_path}")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    # Convert Markdown to basic HTML (simple wrapper)
    html_content = f"""
    <div style="font-family: monospace; white-space: pre-wrap;">
    {report_content}
    </div>
    """

    print(f"📧 Sending report to {TO_EMAIL}...")

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "Empire System <system@resend.dev>",
        "to": [TO_EMAIL],
        "subject": "🏰 Empire Save Protocol: Campaign Report",
        "html": html_content
    }

    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code in [200, 201]:
            print(f"✅ Report Sent! ID: {r.json().get('id')}")
        else:
            print(f"❌ Failed to send email: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Exception sending email: {e}")

if __name__ == "__main__":
    send_report()
