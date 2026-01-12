"""Check enrichment data in leads"""
from supabase import create_client
import os, json
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

# Get sample enriched leads
result = client.table('leads').select('*').eq('status', 'contacted').limit(5).execute()

print('='*60)
print('SAMPLE ENRICHED LEAD DATA')
print('='*60)
for lead in result.data:
    print(f"Company: {lead.get('company_name')}")
    print(f"Status: {lead.get('status')}")
    
    meta = lead.get('agent_research', {})
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except:
            meta = {}
    if meta and isinstance(meta, dict):
        print(f"Decision Maker: {meta.get('decision_maker', 'N/A')}")
        print(f"Enriched Email: {meta.get('enriched_email', 'N/A')}")
        print(f"Enriched Phone: {meta.get('enriched_phone', 'N/A')}")
        print(f"Title: {meta.get('title', 'N/A')}")
        print(f"LinkedIn: {meta.get('linkedin_url', 'N/A')}")
        print(f"All Meta Keys: {list(meta.keys())}")
    else:
        print('No enrichment data')
    print('-'*40)
