"""Quick pipeline check"""
from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# Get today's contacted
contacted = client.table('leads').select('id, company_name').eq('status', 'contacted').gte('updated_at', today.isoformat()).limit(20).execute()

# Get total counts
total = len(client.table('leads').select('id').execute().data)
enriched = len(client.table('leads').select('id').eq('status', 'enriched').execute().data)
needs = len(client.table('leads').select('id').eq('status', 'needs_enrichment').execute().data)
contacted_count = len(contacted.data)

print('='*50)
print('TODAY STATS')
print('='*50)
print(f'Total Leads in Pipeline: {total}')
print(f'Enriched (ready to contact): {enriched}')
print(f'Needs Enrichment: {needs}')
print(f'Contacted TODAY: {contacted_count}')
print()
print('Companies contacted today:')
for lead in contacted.data[:15]:
    company = lead.get("company_name", "Unknown")
    print(f'  - {company}')
