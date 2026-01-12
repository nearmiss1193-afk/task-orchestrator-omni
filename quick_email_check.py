"""Quick email check"""
import requests, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('RESEND_API_KEY')
if key:
    r = requests.get('https://api.resend.com/emails', headers={'Authorization': f'Bearer {key}'})
    if r.status_code == 200:
        emails = r.json().get('data', [])[:5]
        print('=== RECENT EMAILS ===')
        for e in emails:
            to_list = e.get('to', [])
            to_str = to_list[0] if to_list else 'N/A'
            subj = str(e.get('subject', 'N/A'))[:50]
            status = e.get('last_event', 'unknown')
            print(f"  To: {to_str}")
            print(f"  Subject: {subj}")
            print(f"  Status: {status}")
            print()
    else:
        print(f'Error: {r.status_code}')
else:
    print('No RESEND_API_KEY found')
