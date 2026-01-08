"""Quick Resend email check - no complex formatting"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
r = requests.get('https://api.resend.com/emails', headers={'Authorization': f'Bearer {RESEND_API_KEY}'})
print(f"Resend Status: {r.status_code}")
if r.status_code == 200:
    data = r.json().get('data', [])
    print(f"Emails sent: {len(data)}")
    for e in data[:15]:
        print(f"  {e.get('to')} - {e.get('subject','')[:40]}")
else:
    print(r.text[:200])
