"""Check pipeline status"""
from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

# Count by status
print('='*50)
print('CURRENT PIPELINE STATUS')
print('='*50)
statuses = {}
result = client.table('leads').select('status').execute()
for lead in result.data:
    s = lead.get('status', 'unknown')
    statuses[s] = statuses.get(s, 0) + 1

total = sum(statuses.values())
print(f'TOTAL LEADS: {total}')
print()
for s, count in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f'  {s}: {count}')

# Today's activity
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today_leads = client.table('leads').select('id').gte('created_at', today.isoformat()).execute()
today_updated = client.table('leads').select('id').eq('status', 'contacted').gte('updated_at', today.isoformat()).execute()
print()
print(f'NEW LEADS TODAY: {len(today_leads.data)}')
print(f'CONTACTED TODAY: {len(today_updated.data)}')
