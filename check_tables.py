#!/usr/bin/env python3
"""Check if attribution tables exist in Supabase"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}

# Check if outbound_touches table exists
resp = requests.get(f'{SUPABASE_URL}/rest/v1/outbound_touches?limit=1', headers=headers)
if resp.status_code == 200:
    print('outbound_touches: EXISTS')
else:
    print(f'outbound_touches: MISSING ({resp.status_code})')

# Check if outreach_attribution table exists
resp2 = requests.get(f'{SUPABASE_URL}/rest/v1/outreach_attribution?limit=1', headers=headers)
if resp2.status_code == 200:
    print('outreach_attribution: EXISTS')
else:
    print(f'outreach_attribution: MISSING ({resp2.status_code})')
