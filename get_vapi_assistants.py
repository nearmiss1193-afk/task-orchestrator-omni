"""Get Vapi assistants"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

vapi_key = os.getenv('VAPI_PRIVATE_KEY')
print('Fetching Vapi assistants...')

resp = requests.get(
    'https://api.vapi.ai/assistant',
    headers={'Authorization': f'Bearer {vapi_key}'}
)

if resp.status_code == 200:
    assistants = resp.json()
    print(f'Found {len(assistants)} assistants:')
    for a in assistants[:10]:
        print(f"  {a.get('id')} | {a.get('name', 'N/A')}")
else:
    print(f'Error: {resp.status_code} - {resp.text[:200]}')
