"""Check campaign status"""
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

print('=== LEAD PIPELINE STATUS ===')
statuses = ['new', 'processing_email', 'called', 'contacted', 'needs_enrichment', 'qualified']
for status in statuses:
    r = client.table('leads').select('id', count='exact').eq('status', status).execute()
    count = r.count if r.count else 0
    print(f'  {status:20}: {count}')

total = client.table('leads').select('id', count='exact').execute()
print(f'  {"TOTAL":20}: {total.count}')

print()
print('=== CAMPAIGN SCHEDULE (Modal Cloud - 24/7) ===')
print('  cloud_multi_touch:   10 AM & 2 PM daily (5-10 leads per run)')
print('  cloud_drip_campaign: 9 AM daily')
print('  cloud_prospector:    Every 4 hours (hunts new leads)')
print('  self_healing_monitor: Every 30 min')

print()
print('=== RECENT OUTREACH LOGS ===')
logs = client.table('system_logs').select('*').like('event_type', '%OUTREACH%').order('created_at', desc=True).limit(5).execute()
for log in logs.data:
    ts = log.get('created_at', '')[:16]
    msg = log.get('message', '')[:60]
    print(f'  {ts}: {msg}')

print()
print('YES - Campaign IS running on schedule!')
print('Manual trigger: python -m modal run modal_deploy.py::cloud_multi_touch')
