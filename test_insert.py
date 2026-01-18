#!/usr/bin/env python3
"""Test insert into outbound_touches"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
headers = {
    'apikey': SUPABASE_KEY, 
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Try inserting a test touch
touch = {
    "phone": "+13529368152",
    "channel": "sms",
    "variant_id": "variant_a",
    "variant_name": "Direct CTA",
    "run_id": "test_jan18",
    "status": "sent"
}

resp = requests.post(f'{SUPABASE_URL}/rest/v1/outbound_touches', headers=headers, json=touch)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text}')

if resp.status_code in [200, 201]:
    print('SUCCESS!')
else:
    print('FAILED - check RLS policies')
