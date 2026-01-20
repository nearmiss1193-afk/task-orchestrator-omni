import os
import requests
from dotenv import load_dotenv

load_dotenv()
VAPI_KEY = os.getenv('VAPI_PRIVATE_KEY') or os.getenv('VAPI_API_KEY')
SARAH_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'

headers = {'Authorization': f'Bearer {VAPI_KEY}', 'Content-Type': 'application/json'}

# First, get current Sarah config
print('=== FETCHING CURRENT SARAH CONFIG ===')
r = requests.get(f'https://api.vapi.ai/assistant/{SARAH_ID}', headers=headers)
if r.status_code != 200:
    print(f'Error fetching: {r.status_code} - {r.text}')
    exit(1)

sarah = r.json()
print(f"Name: {sarah.get('name')}")
current_prompt = sarah.get('model', {}).get('systemPrompt', '')
print(f'Current prompt length: {len(current_prompt)} chars')

# Update with Spanish
spanish_addition = """

## BILINGUAL SUPPORT
You are fluent in both English and Spanish. If the caller speaks Spanish, respond entirely in Spanish. Detect the language from the caller's speech and respond accordingly."""

new_prompt = current_prompt + spanish_addition

print('\n=== UPDATING WITH SPANISH ===')
update_payload = {
    'model': {
        **sarah.get('model', {}),
        'systemPrompt': new_prompt
    }
}

r2 = requests.patch(f'https://api.vapi.ai/assistant/{SARAH_ID}', headers=headers, json=update_payload)
if r2.status_code == 200:
    print('SUCCESS! Sarah updated with Spanish capability')
    updated = r2.json()
    new_len = len(updated.get('model', {}).get('systemPrompt', ''))
    print(f'New prompt length: {new_len} chars')
else:
    print(f'Error updating: {r2.status_code} - {r2.text}')
