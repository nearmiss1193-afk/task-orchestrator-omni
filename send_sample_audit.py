"""
Send sample audit email to user for verification
"""
import requests

# GHL Webhooks
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/cf2e8a9c-e943-4d78-9f6f-cd66bb9a2e42"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Sample data
company_name = "Midwest Climate Control"
audit_link = "https://www.aiserviceco.com/audits/midwest-climate-control-4813fdb0.html"
missed_revenue = 144000

# Email content
subject = f"ALERT - {company_name}: We Found ${missed_revenue:,} You're Missing"
body = f"""Hi,

I ran a free website and phone audit for {company_name}.

**Your Custom Report:** {audit_link}

Key Finding: Our analysis shows you're potentially leaving ${missed_revenue:,}/year on the table due to missed calls and manual scheduling.

I'd love to show you how we can fix this in 15 minutes.

Reply to this email or call (863) 337-3705.

Best,
Sarah
AI Service Co
"""

# Send email to user
print("=" * 50)
print("SENDING SAMPLE AUDIT EMAIL")
print("=" * 50)

email_resp = requests.post(GHL_EMAIL_WEBHOOK, json={
    "email": "nearmiss1193@gmail.com",
    "subject": subject,
    "body": body
}, timeout=15)

print(f"\n[EMAIL]")
print(f"  To: nearmiss1193@gmail.com")
print(f"  Subject: {subject}")
print(f"  Status: {email_resp.status_code}")
print(f"  Response: {email_resp.text[:100] if email_resp.text else 'OK'}")

# Also send SMS sample
sms_msg = f"Hi! Just finished an audit for {company_name}. Found opportunities: {audit_link} - Reply for free consultation. -Sarah"

sms_resp = requests.post(GHL_SMS_WEBHOOK, json={
    "phone": "+13527585336",  # User's number
    "message": sms_msg
}, timeout=15)

print(f"\n[SMS]")
print(f"  To: +13527585336")
print(f"  Message: {sms_msg[:80]}...")
print(f"  Status: {sms_resp.status_code}")
print(f"  Response: {sms_resp.text[:100] if sms_resp.text else 'OK'}")

print("\n" + "=" * 50)
print("CHECK YOUR EMAIL AND PHONE FOR SAMPLES")
print("=" * 50)
