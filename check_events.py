#!/usr/bin/env python3
"""Check event_log_v2 for learning verification"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')

headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}

# Get last 50 events
resp = requests.get(f'{SUPABASE_URL}/rest/v1/event_log_v2?select=type,ts,entity_id,payload&order=ts.desc&limit=50', headers=headers)
events = resp.json() if resp.status_code == 200 else []

# Count by type
type_counts = {}
for e in events:
    t = e.get('type', 'unknown')
    type_counts[t] = type_counts.get(t, 0) + 1

print('=== LAST 50 EVENTS BY TYPE ===')
for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f'  {t}: {c}')

print()
print('=== RECENT 15 EVENTS ===')
for e in events[:15]:
    ts = e.get('ts', '')[:19] if e.get('ts') else '--'
    etype = e.get('type', '')
    eid = (e.get('entity_id') or '')[:25]
    print(f'{ts} | {etype} | {eid}')

# Check for variant tracking
print()
print('=== VARIANT TRACKING ===')
variant_events = [e for e in events if e.get('payload') and (
    e['payload'].get('variant_id') or 
    e['payload'].get('variant_name') or 
    e['payload'].get('ab_variant')
)]
print(f'Events with variant data: {len(variant_events)}')

# Check for appointment events
print()
print('=== APPOINTMENT EVENTS ===')
appt_events = [e for e in events if 'appointment' in e.get('type', '').lower()]
print(f'Appointment events in last 50: {len(appt_events)}')
for e in appt_events[:5]:
    print(f"  {e.get('type')} @ {e.get('ts', '')[:19]}")

# Check for SMS events
print()
print('=== SMS EVENTS ===')
sms_events = [e for e in events if 'sms' in e.get('type', '').lower()]
print(f'SMS events in last 50: {len(sms_events)}')
for e in sms_events[:5]:
    print(f"  {e.get('type')} @ {e.get('ts', '')[:19]}")
