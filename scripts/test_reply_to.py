"""Test #3: Send from owner@aiserviceco.com - the real test"""
import os, requests
from dotenv import load_dotenv
load_dotenv()

resend_key = os.getenv('RESEND_API_KEY')

payload = {
    'from': 'Dan <owner@aiserviceco.com>',
    'reply_to': 'owner@aiserviceco.com',
    'to': ['owner@aiserviceco.com'],
    'subject': 'TEST #3: Reply should work now - hit reply!',
    'html': (
        '<div style="font-family: Arial; font-size: 14px; color: #333;">'
        '<p>Hey Dan,</p>'
        '<p>This email is now sent FROM <strong>owner@aiserviceco.com</strong> (your real inbox).</p>'
        '<p>Hit <strong>Reply</strong> and send anything back. It should land right in your inbox this time.</p>'
        '<p>- Antigravity</p>'
        '</div>'
    ),
}

r = requests.post(
    'https://api.resend.com/emails',
    headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
    json=payload,
    timeout=15
)
print('Status:', r.status_code)
if r.status_code in [200, 201]:
    print('SENT - check your inbox and hit Reply')
else:
    print('FAILED:', r.text[:200])
