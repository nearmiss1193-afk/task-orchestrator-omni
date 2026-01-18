#!/usr/bin/env python3
"""Check SMS events in detail"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')

headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
resp = requests.get(f'{SUPABASE_URL}/rest/v1/event_log_v2?select=type,ts,payload&order=ts.desc&limit=200', headers=headers)
events = resp.json() if resp.status_code == 200 else []

sms_types = [e for e in events if 'sms' in e.get('type', '').lower()]
print(f'SMS EVENTS FOUND: {len(sms_types)}')
for e in sms_types[:10]:
    ts = e.get('ts', '')[:19] if e.get('ts') else '--'
    etype = e.get('type', '')
    print(f'  {etype} @ {ts}')
