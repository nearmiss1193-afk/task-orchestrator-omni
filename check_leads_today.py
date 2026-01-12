"""Check lead pipeline status"""
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

# Get leads from today
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
result = client.table('leads').select('id, company_name, status, created_at').gte('created_at', today.isoformat()).order('created_at', desc=True).limit(20).execute()

print('='*60)
print('LEADS CREATED TODAY')
print('='*60)
print(f'Total: {len(result.data)}')
for lead in result.data:
    created = lead.get('created_at', '')[:16]
    company = lead.get("company_name", "Unknown")[:40]
    status = lead.get("status", "?")
    print(f"  {created} | {status:<15} | {company}")

# Get pipeline status
print()
print('PIPELINE SUMMARY:')
statuses = {}
for lead in client.table('leads').select('status').execute().data:
    s = lead.get('status', 'unknown')
    statuses[s] = statuses.get(s, 0) + 1
for s, count in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f"  {s}: {count}")
