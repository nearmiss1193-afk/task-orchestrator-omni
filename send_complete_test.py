"""
Send complete test - Email via Resend + SMS via GHL with working Manus link
"""
import requests

# Working link from Manus
WORKING_AUDIT_LINK = "https://hvacreports-6e2qqkhj.manus.space/"
COMPANY = "Midwest Climate Control"

# Resend for email (confirmed working)
RESEND_API_KEY = "re_6q5Rx16W_NJbL5MjDAzf9FhGEEBqhcfrm"

# GHL for SMS (confirmed working)
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

print("=" * 60)
print("SENDING TEST EMAIL + SMS WITH WORKING LINK")
print("=" * 60)

# Send Email via Resend
print("\n[1] Sending Email via Resend...")
email_resp = requests.post(
    "https://api.resend.com/emails",
    headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
    json={
        "from": "Sarah <sarah@aiserviceco.com>",
        "to": ["nearmiss1193@gmail.com"],
        "subject": f"ALERT - {COMPANY}: We Found $144,000 You're Missing",
        "html": f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #3b82f6;">Your Marketing Audit is Ready!</h2>
    
    <p>Hi!</p>
    
    <p>I ran a free website and phone audit for <strong>{COMPANY}</strong>.</p>
    
    <p><strong>📊 Your Custom Report:</strong> <a href="{WORKING_AUDIT_LINK}" style="color: #3b82f6; font-size: 16px;">{WORKING_AUDIT_LINK}</a></p>
    
    <p><strong>Key Finding:</strong> Our analysis shows you're potentially leaving <span style="color: #ef4444; font-weight: bold;">$144,000/year</span> on the table due to missed calls and manual scheduling.</p>
    
    <p>I'd love to show you how we can fix this in 15 minutes.</p>
    
    <p>Reply to this email or call <strong>(863) 337-3705</strong>.</p>
    
    <p>Best,<br>
    <strong>Sarah</strong><br>
    AI Service Co</p>
</div>
"""
    },
    timeout=15
)
print(f"  Status: {email_resp.status_code}")
print(f"  Result: {'OK' if email_resp.status_code == 200 else email_resp.text[:100]}")

# Send SMS via GHL
print("\n[2] Sending SMS via GHL...")
sms_resp = requests.post(
    GHL_SMS_WEBHOOK,
    json={
        "phone": "+13527585336",
        "message": f"Hi! Just finished an audit for {COMPANY}. Found $144K opportunity. Check it out: {WORKING_AUDIT_LINK} - Reply for free consultation. -Sarah"
    },
    timeout=15
)
print(f"  Status: {sms_resp.status_code}")
print(f"  Result: {'OK' if sms_resp.status_code == 200 else sms_resp.text[:100]}")

print("\n" + "=" * 60)
print("CHECK YOUR EMAIL AND PHONE")
print(f"Link: {WORKING_AUDIT_LINK}")
print("=" * 60)
