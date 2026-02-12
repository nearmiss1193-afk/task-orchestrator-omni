"""Get the 10 most recent calls to find Dan's latest"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

r = requests.get('https://api.vapi.ai/call?limit=10', headers=headers)
calls = r.json()

print(f"Total calls returned: {len(calls)}")
for i, c in enumerate(calls):
    created = c.get('createdAt', '?')[:19]
    ended = c.get('endedAt', '?')
    ended_str = ended[:19] if ended else 'still active'
    customer = c.get('customer', {}).get('number', '?')
    server_url = c.get('serverUrl')
    server_url_str = server_url[:50] if server_url else 'NULL'
    msgs = c.get('messages', [])
    msg_count = len(msgs) if msgs else 0
    
    print(f"\n[{i+1}] {c.get('id', '?')}")
    print(f"    Created: {created} | Ended: {ended_str}")
    print(f"    Customer: {customer}")
    print(f"    ServerUrl: {server_url_str}")
    print(f"    Messages: {msg_count}")
    print(f"    EndedReason: {c.get('endedReason', '?')}")
