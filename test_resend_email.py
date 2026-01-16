"""
Test email sending via Resend directly
This bypasses GHL to confirm emails can be sent
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')

if not RESEND_API_KEY:
    print("[ERROR] RESEND_API_KEY not found in .env")
    exit(1)

print(f"Resend Key: {RESEND_API_KEY[:20]}...")

# Use Manus report link (working) for now
audit_link = "https://hvacreports-6e2qqkhj.manus.space/"

resp = requests.post(
    'https://api.resend.com/emails',
    headers={
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json'
    },
    json={
        'from': 'Sarah <sarah@aiserviceco.com>',
        'to': ['nearmiss1193@gmail.com'],
        'subject': 'TEST - Your HVAC Marketing Audit Report',
        'html': f'''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #3b82f6;">Your Marketing Audit is Ready!</h2>
    
    <p>Hi!</p>
    
    <p>I ran a free website and phone audit for <strong>Midwest Climate Control</strong>.</p>
    
    <p><strong>📊 Your Custom Report:</strong> <a href="{audit_link}" style="color: #3b82f6;">{audit_link}</a></p>
    
    <p><strong>Key Finding:</strong> Our analysis shows you're potentially leaving <span style="color: #ef4444; font-weight: bold;">$144,000/year</span> on the table due to missed calls and manual scheduling.</p>
    
    <p>I'd love to show you how we can fix this in 15 minutes.</p>
    
    <p>Reply to this email or call <strong>(863) 337-3705</strong>.</p>
    
    <p>Best,<br>
    <strong>Sarah</strong><br>
    AI Service Co</p>
</div>
'''
    },
    timeout=15
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
