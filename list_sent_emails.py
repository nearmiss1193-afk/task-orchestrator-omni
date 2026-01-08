"""Get detailed Resend email list"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
r = requests.get('https://api.resend.com/emails', headers={'Authorization': f'Bearer {RESEND_API_KEY}'})

if r.status_code == 200:
    data = r.json().get('data', [])
    print(f"Total emails: {len(data)}\n")
    
    # Extract unique recipients
    recipients = set()
    for e in data:
        to = e.get('to', [])
        if isinstance(to, list):
            for addr in to:
                recipients.add(addr)
        else:
            recipients.add(to)
    
    print("UNIQUE RECIPIENTS (avoid duplicates):")
    for r in sorted(recipients):
        print(f"  - {r}")
    
    print(f"\nTotal unique: {len(recipients)}")
