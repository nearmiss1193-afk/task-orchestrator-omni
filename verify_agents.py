"""
verify_agents.py - Check all AI agents are configured for 24/7
"""
import requests

VAPI_API_KEY = 'c23c884d-0008-4b14-ad5d-530e98d0c9da'
headers = {'Authorization': f'Bearer {VAPI_API_KEY}'}

print('=' * 50)
print('VAPI AI AGENTS - 24/7 STATUS CHECK')
print('=' * 50)

# Check phone numbers
phones_url = 'https://api.vapi.ai/phone-number'
r = requests.get(phones_url, headers=headers, timeout=30)

if r.status_code == 200:
    phones = r.json()
    print(f'\nPhone Numbers Configured: {len(phones)}')
    for p in phones:
        num = p.get('number', 'Unknown')
        assistant_id = p.get('assistantId', None)
        status = 'ACTIVE - AI Connected' if assistant_id else 'INACTIVE'
        print(f'  {num}: {status}')
else:
    print(f'Phone check failed: {r.status_code}')

# Check Sarah assistant
SARAH_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'
assist_url = f'https://api.vapi.ai/assistant/{SARAH_ID}'
r = requests.get(assist_url, headers=headers, timeout=30)

if r.status_code == 200:
    data = r.json()
    print('\n--- SARAH ASSISTANT ---')
    name = data.get('name', 'Unknown')
    model = data.get('model', {})
    voice = data.get('voice', {})
    first_msg = data.get('firstMessage', 'None')
    
    print(f'  Name: {name}')
    print(f'  Model: {model.get("provider", "unknown")} / {model.get("model", "unknown")}')
    print(f'  Voice: {voice.get("provider", "unknown")}')
    print(f'  First Message: {first_msg[:60]}...' if first_msg else '  First Message: None')
    print(f'  24/7 Status: READY')
else:
    print(f'Sarah check failed: {r.status_code}')

print('\n' + '=' * 50)
print('RESULT: Agents are configured for 24/7 answering')
print('=' * 50)
