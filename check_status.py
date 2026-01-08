"""Check Resend sent emails and GHL SMS status"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Check Resend
print("="*60)
print("RESEND - SENT EMAILS")
print("="*60)

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
headers = {'Authorization': f'Bearer {RESEND_API_KEY}'}

r = requests.get('https://api.resend.com/emails', headers=headers)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    emails = r.json().get('data', [])
    print(f'Total emails found: {len(emails)}')
    for email in emails[:20]:
        to = email.get('to', ['N/A'])
        to_str = to[0] if isinstance(to, list) else to
        subject = email.get('subject', 'N/A')[:50]
        created = email.get('created_at', 'N/A')[:19]
        print(f"  {to_str} | {subject} | {created}")
else:
    print(f'Error: {r.text[:300]}')

# Check GHL conversations
print("\n" + "="*60)
print("GHL - RECENT CONVERSATIONS")  
print("="*60)

GHL_API_KEY = os.getenv('GHL_API_KEY')
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID')

headers = {
    'Authorization': f'Bearer {GHL_API_KEY}',
    'Content-Type': 'application/json',
    'Version': '2021-07-28'
}

url = f'https://services.leadconnectorhq.com/conversations/search?locationId={GHL_LOCATION_ID}'
r = requests.get(url, headers=headers)
print(f'API Status: {r.status_code}')
if r.status_code == 200:
    convos = r.json().get('conversations', [])
    print(f'Found {len(convos)} conversations')
    for c in convos[:10]:
        name = c.get('contactName', 'Unknown')
        msg_type = c.get('lastMessageType', 'N/A')
        date = str(c.get('lastMessageDate', 'N/A'))[:19]
        print(f"  {name} | {msg_type} | {date}")
elif r.status_code == 401:
    print("401 Unauthorized - GHL API token may be expired or invalid")
else:
    print(f'Error: {r.text[:300]}')

# Check GHL contacts to see if test contact was created
print("\n" + "="*60)
print("GHL - CONTACTS (checking if webhook created contact)")
print("="*60)

url = f'https://services.leadconnectorhq.com/contacts/?locationId={GHL_LOCATION_ID}&query=352'
r = requests.get(url, headers=headers)
print(f'Contacts search: {r.status_code}')
if r.status_code == 200:
    contacts = r.json().get('contacts', [])
    print(f'Found {len(contacts)} contacts matching 352')
    for c in contacts[:5]:
        print(f"  {c.get('phone', 'N/A')} | {c.get('firstName', '')} {c.get('lastName', '')} | {c.get('email', 'N/A')}")
else:
    print(f'Error: {r.text[:200]}')
