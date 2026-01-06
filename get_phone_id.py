#!/usr/bin/env python3
"""Get just the phone ID"""
import requests

key = None
with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'VAPI_PRIVATE_KEY' in line and '=' in line:
            key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

r = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {key}'})
phones = r.json()
if phones:
    print(f"PHONE_ID={phones[0].get('id')}")
    print(f"NUMBER={phones[0].get('number')}")
