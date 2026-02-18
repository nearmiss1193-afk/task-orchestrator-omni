
import os
import json
from supabase import create_client

def check_results():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    sb = create_client(url, key)
    
    res = sb.table('contacts_master').select('id,raw_research').order('created_at', desc=True).limit(1000).execute()
    matches = 0
    priority_leads = []
    
    processed = 0
    for r in res.data:
        rr = r.get('raw_research')
        if not rr: continue
        if isinstance(rr, str):
            try: rr = json.loads(rr)
            except: continue
        
        if rr.get('extraction_ts') or rr.get('principal_matches'):
            processed += 1
            if rr.get('is_priority_owner'):
                matches += 1
                priority_leads.append(r['id'])
            
    print(f"Total leads audited: {len(res.data)}")
    print(f"Leads processed by worker: {processed}")
    print(f"Priority matches found: {matches}")
    if matches > 0:
        print(f"Sample Priority IDs: {priority_leads[:5]}")

if __name__ == "__main__":
    check_results()
