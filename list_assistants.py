#!/usr/bin/env python3
"""Get all Vapi assistants"""
import requests

key = None
with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'VAPI_PRIVATE_KEY' in line and '=' in line:
            key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

r = requests.get('https://api.vapi.ai/assistant', headers={'Authorization': f'Bearer {key}'})
assts = r.json()
print('VAPI ASSISTANTS:')
print('='*50)
for a in assts:
    print(f"Name: {a.get('name')}")
    print(f"  ID: {a.get('id')}")
    print()
