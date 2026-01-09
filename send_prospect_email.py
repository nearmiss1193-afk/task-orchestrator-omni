"""
SEND CUSTOMIZED PROSPECT EMAIL (HOMEHEART HVAC)
Uses Resend API for reliable delivery
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')

if not RESEND_API_KEY:
    print("❌ RESEND_API_KEY not found")
    exit(1)

# --- PROSPECT DETAILS ---
PROSPECT_EMAIL = "seaofdiscipline@gmail.com"
PROSPECT_NAME = "Homeheart"
COMPANY_NAME = "Homeheart HVAC & Cool"

# Video asset link (host on aiserviceco.com or public CDN)
VIDEO_LINK = "https://aiserviceco.com/assets/missed_call_rescue.mp4"

EMAIL_SUBJECT = f"Quick look at this for {COMPANY_NAME}"

EMAIL_HTML = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px; }}
        h1 {{ color: #3b82f6; margin-bottom: 24px; }}
        p {{ font-size: 16px; line-height: 1.6; margin: 16px 0; }}
        .cta {{ display: inline-block; background: #2563eb; color: white; padding: 16px 32px; border-radius: 10px; text-decoration: none; font-weight: bold; margin: 24px 0; }}
        .cta:hover {{ background: #1d4ed8; }}
        .stat {{ background: #334155; padding: 12px 20px; border-radius: 8px; margin: 12px 0; border-left: 4px solid #3b82f6; }}
        .footer {{ color: #94a3b8; font-size: 13px; margin-top: 32px; border-top: 1px solid #334155; padding-top: 16px; }}
        a {{ color: #3b82f6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Quick Video for {PROSPECT_NAME}</h1>
        
        <p>Hey {PROSPECT_NAME},</p>

        <p>I put together a quick 60-second breakdown of what happens when your phones go unanswered at 2 AM:</p>

        <a href="{VIDEO_LINK}" class="cta">▶️ Watch the Missed Call Rescue Video</a>

        <div class="stat">
            <strong>78%</strong> of customers hire the first company that responds.
        </div>
        
        <div class="stat">
            <strong>40%</strong> of service calls go to voicemail industry-wide.
        </div>

        <p>If you want a system that treats every lead like a winning lottery ticket—while you're out making money—let's chat.</p>

        <a href="https://www.aiserviceco.com/features.html" class="cta" style="background: #22c55e;">📅 Book a Quick Demo Call</a>

        <p>Talk soon,<br>
        <strong>Daniel @ AI Service Co</strong></p>

        <div class="footer">
            <p>AI Service Co | <a href="https://aiserviceco.com">aiserviceco.com</a></p>
        </div>
    </div>
</body>
</html>
"""

# --- SEND EMAIL ---
print(f"📧 Sending customized prospect email to {PROSPECT_NAME} ({PROSPECT_EMAIL})...")

res = requests.post(
    'https://api.resend.com/emails',
    headers={
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json'
    },
    json={
        'from': 'Empire System <system@aiserviceco.com>',
        'reply_to': 'owner@aiserviceco.com',
        'to': PROSPECT_EMAIL,
        'subject': EMAIL_SUBJECT,
        'html': EMAIL_HTML
    },
    timeout=15
)

if res.status_code == 200:
    print(f"✅ EMAIL SENT TO {PROSPECT_EMAIL}")
    print(f"Response: {res.json()}")
else:
    print(f"❌ Failed: {res.status_code}")
    print(res.text)
