"""Check email delivery status"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

resend_key = os.getenv('RESEND_API_KEY')

print("=" * 60)
print("EMAIL DELIVERY CHECK")
print("=" * 60)

# Get recent emails
response = requests.get(
    'https://api.resend.com/emails',
    headers={'Authorization': f'Bearer {resend_key}'},
    params={'limit': 15}
)

if response.status_code == 200:
    data = response.json()
    emails = data.get('data', [])
    print(f'\nRecent {len(emails)} emails from Resend:')
    print("-" * 60)
    for e in emails:
        created = e.get('created_at', 'N/A')[:16]
        to = e.get('to', ['N/A'])[0][:30]
        subject = e.get('subject', 'N/A')[:35]
        last_event = e.get('last_event', 'N/A')
        print(f"{created} | {to:30} | {last_event:10} | {subject}")
else:
    print(f'Error: {response.status_code} - {response.text[:200]}')

print()
print("=" * 60)
print("last_event meanings:")
print("  sent = Email accepted by Resend")
print("  delivered = Confirmed delivered to inbox")
print("  bounced = Email bounced")
print("  complained = Marked as spam")
print("=" * 60)
