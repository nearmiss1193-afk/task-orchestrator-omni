"""Quick email test with Resend API key from .env"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

RESEND_KEY = os.getenv("RESEND_API_KEY", "re_6q5Rx16W_NJbL5MjDAzf9FhGEEBqhcfrm")
print(f"Using key: {RESEND_KEY[:20]}...")

# Simple test email
resp = requests.post(
    "https://api.resend.com/emails",
    headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
    json={
        "from": "Sarah <sarah@aiserviceco.com>",
        "to": ["nearmiss1193@gmail.com"],
        "subject": "[PRIVATE] Your Marketing Audit - Midwest Climate Control",
        "html": """
<div style="font-family:Arial;padding:20px;max-width:600px;margin:0 auto;">
<h2 style="color:#1e40af;">Your Marketing Audit is Ready!</h2>
<p>Hi,</p>
<p>I just completed a comprehensive audit for <strong>Midwest Climate Control</strong>.</p>
<p style="background:#fef3c7;padding:15px;border-left:4px solid #f59e0b;">
<strong>Key Finding:</strong> You're missing an estimated <strong>$144,000/year</strong> due to missed calls and lack of online booking.
</p>
<p><a href="https://www.aiserviceco.com/audits/midwest-climate-control-demo.html" style="background:#3b82f6;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;">View Your Private Report</a></p>
<p>Reply to this email or call <strong>(863) 337-3705</strong>.</p>
<p>Best,<br><strong>Sarah</strong><br>AI Service Co</p>
</div>
"""
    },
    timeout=15
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
