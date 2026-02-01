"""
Reliable Email Sender with Multiple Fallbacks
Used by save_protocol and outreach verification
"""
import os
import requests
from datetime import datetime

# Email destinations
OWNER_EMAIL = "nearmiss1193@gmail.com"

# Provider 1: GHL Webhook
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

# Provider 2: Resend Direct API
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy")

def send_email(to_email, subject, html_body, from_name="Empire System", tags=None):
    """Send email with automatic fallback
    
    1. Try Resend (most reliable)
    2. Try GHL Webhook (backup)
    3. Log failure if both fail
    """
    success = False
    provider_used = None
    
    # TRY 1: Resend Direct (PRIMARY)
    try:
        payload = {
            "from": "Empire System <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }
        if tags:
            payload["tags"] = tags

        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json=payload,
            timeout=30
        )
        if r.ok:
            print(f"[EMAIL] ✅ Sent via Resend to {to_email}")
            return {"success": True, "provider": "resend", "response": r.json()}
        else:
            print(f"[EMAIL] ⚠️ Resend failed: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"[EMAIL] ⚠️ Resend exception: {e}")

    # TRY 2: GHL Webhook (BACKUP)
    try:
        r = requests.post(
            GHL_EMAIL_WEBHOOK,
            json={
                "email": to_email,
                "from_name": from_name,
                "from_email": "system@aiserviceco.com",
                "subject": subject,
                "html_body": html_body
            },
            timeout=30
        )
        if r.ok:
            print(f"[EMAIL] ✅ Sent via GHL to {to_email}")
            return {"success": True, "provider": "ghl", "response": r.text}
        else:
            print(f"[EMAIL] ❌ GHL failed: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"[EMAIL] ❌ GHL exception: {e}")
    
    print(f"[EMAIL] ❌ ALL PROVIDERS FAILED for {to_email}")
    return {"success": False, "provider": None, "error": "All providers failed"}


def send_session_summary():
    """Send current session summary to owner"""
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    html = f"""
    <h2>📊 SESSION SUMMARY - {now}</h2>
    
    <p><b>Dashboard:</b> <a href="https://www.aiserviceco.com/dashboard.html">aiserviceco.com/dashboard.html</a></p>
    
    <h3>🚀 System Capabilities</h3>
    <ul>
        <li><b>Prospecting:</b> Automated scraping & enrichment (Lusha/Apollo) save to Supabase.</li>
        <li><b>Outreach:</b> 24/7 autonomous email (Resend/GHL) & SMS (Business Hours).</li>
        <li><b>Voice AI:</b> "Sarah" (Vapi) autonomous calling (20 calls/hr target).</li>
        <li><b>Infrastructure:</b> Self-healing Railway workers, Supabase DB, Next.js Portal.</li>
    </ul>

    <h3>🔄 Operational Processes</h3>
    <ul>
        <li><b>Auto-Scheduler:</b> Runs prospector/outreach every 10m, calls every 3m.</li>
        <li><b>Error Recovery:</b> <code>safe_run</code> wrapper catches crashes; <code>/health</code> restarts frozen threads.</li>
        <li><b>Deployment:</b> Git Push → Railway Build → Auto-Restart.</li>
    </ul>

    <h3>💡 Recommendations</h3>
    <ul>
        <li><b>Immediate:</b> Fix GHL "Email Outreach" workflow (currently Draft).</li>
        <li><b>Database:</b> Add <code>phone</code> column to Supabase leads table.</li>
        <li><b>Verification:</b> Monitor "BCC" emails to ensure Resend delivery.</li>
    </ul>
    
    <h3>🛠️ Recovery Commands</h3>
    <pre>
curl https://empire-unified-backup-production.up.railway.app/stats
curl -X POST https://empire-unified-backup-production.up.railway.app/trigger/outreach
    </pre>
    
    <p>- Empire System</p>
    """
    
    return send_email(OWNER_EMAIL, f"📊 SESSION SUMMARY - {now}", html)


def send_outreach_verification(email_sent_to, company_name, email_content):
    """Send copy of outreach email to owner for verification"""
    now = datetime.now().strftime("%H:%M")
    
    html = f"""
    <h3>📧 OUTREACH SENT [{now}]</h3>
    <p><b>To:</b> {email_sent_to}</p>
    <p><b>Company:</b> {company_name}</p>
    <hr>
    <div style="border-left: 3px solid #ccc; padding-left: 10px; margin: 10px 0;">
    {email_content}
    </div>
    """
    
    return send_email(OWNER_EMAIL, f"📧 SENT: {company_name} ({email_sent_to})", html)


if __name__ == "__main__":
    print("Testing reliable email sender...")
    result = send_session_summary()
    print(f"Result: {result}")
