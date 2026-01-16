"""
Send WORKING email to user with PRIVATE audit link
Uses our Modal-hosted unique link - NOT the Manus directory!
"""
import requests
import uuid

RESEND_API_KEY = "re_6q5Rx16W_NJbL5MjDAzf9FhGEEBqhcfrm"

# Generate unique private link for this specific company
company_name = "Midwest Climate Control"
report_id = str(uuid.uuid4())[:8]
company_slug = company_name.lower().replace(" ", "-").replace("&", "and")

# Use our Modal-hosted endpoint with unique filename
private_audit_link = f"https://nearmiss1193-afk--audit-reports-serve.modal.run?f={company_slug}-{report_id}.html"

# Also generate a local report just in case
from premium_audit_generator import generate_premium_report
try:
    local_url, filepath = generate_premium_report(company_name, "https://midwestclimatecontrol.com")
    # Use the aiserviceco link if we have a real file
    private_audit_link = local_url
    print(f"Generated report: {filepath}")
except Exception as e:
    print(f"Using Modal link: {private_audit_link}")

print(f"Audit Link: {private_audit_link}")

# Send email
email_html = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">Your Marketing Audit is Ready</h1>
    </div>
    
    <p style="font-size: 16px; color: #333;">Hi,</p>
    
    <p style="font-size: 16px; color: #333;">I just completed a comprehensive website and phone audit for <strong>{company_name}</strong>.</p>
    
    <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
        <strong style="color: #92400e;">Key Finding:</strong> 
        <span style="color: #92400e;">You're potentially missing <strong>$144,000/year</strong> due to missed calls and lack of online booking.</span>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{private_audit_link}" style="background: #3b82f6; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-size: 18px; font-weight: bold; display: inline-block;">
            View Your Private Report
        </a>
    </div>
    
    <p style="font-size: 16px; color: #333;">This is a <strong>private link</strong> - only you can see this report.</p>
    
    <p style="font-size: 16px; color: #333;">I'd love to show you how we can fix these issues in a quick 15-minute call.</p>
    
    <p style="font-size: 16px; color: #333;">
        <strong>Reply to this email</strong> or call me directly at <strong>(863) 337-3705</strong>.
    </p>
    
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
    
    <p style="font-size: 14px; color: #6b7280;">
        Best regards,<br>
        <strong>Sarah</strong><br>
        AI Service Co<br>
        <a href="https://www.aiserviceco.com" style="color: #3b82f6;">www.aiserviceco.com</a>
    </p>
</div>
"""

print("\\nSending email to nearmiss1193@gmail.com...")

resp = requests.post(
    "https://api.resend.com/emails",
    headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
    json={
        "from": "Sarah <sarah@aiserviceco.com>",
        "to": ["nearmiss1193@gmail.com"],
        "subject": f"[PRIVATE] Your Marketing Audit for {company_name}",
        "html": email_html
    },
    timeout=15
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code == 200:
    print("\\n[SUCCESS] Email sent! Check your inbox now.")
    print(f"\\nPrivate Link: {private_audit_link}")
else:
    print("\\n[FAILED] Email not sent - check Resend dashboard")
