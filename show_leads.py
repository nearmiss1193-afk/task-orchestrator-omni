"""Show first 5 leads being processed"""
from supabase import create_client
import os, re, json
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

# Get first 5 leads to see what's being processed
result = client.table('leads').select('id,company_name,phone,agent_research,status').in_('status', ['new', 'processing_email']).limit(5).execute()

print('FIRST 5 LEADS (what cloud_multi_touch sees):')
for i, lead in enumerate(result.data, 1):
    company = lead.get('company_name', 'N/A')[:30]
    phone = lead.get('phone', '')
    ar = lead.get('agent_research', {})
    if isinstance(ar, str):
        try: 
            ar = json.loads(ar)
        except: 
            ar = {}
    rp = ar.get('phone', '') if ar else ''
    actual = phone or rp or 'NONE'
    cleaned = re.sub(r'\D', '', str(actual))
    # Check exchange position
    if len(cleaned) >= 10:
        exchange = cleaned[-7:-4]
        valid = exchange != '555'
    else:
        valid = False
    print(f"{i}. ID={lead.get('id')}: {company:30} | {actual:15} | {'VALID' if valid else 'INVALID'}")

# Count totals
all_leads = client.table('leads').select('*').in_('status', ['new', 'processing_email']).execute()
valid_count = 0
for lead in all_leads.data:
    phone = lead.get('phone', '')
    ar = lead.get('agent_research', {})
    if isinstance(ar, str):
        try: ar = json.loads(ar)
        except: ar = {}
    rp = ar.get('phone', '') if ar else ''
    actual = phone or rp
    if actual:
        cleaned = re.sub(r'\D', '', str(actual))
        if len(cleaned) >= 10:
            exchange = cleaned[-7:-4]
            if exchange != '555':
                valid_count += 1

print(f"\nTotal valid callable: {valid_count} / {len(all_leads.data)}")
