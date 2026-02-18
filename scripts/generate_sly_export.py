
import os
import json
import csv
from datetime import datetime
from supabase import create_client

def generate_sly_export():
    """
    Generates a CSV export of priority "Husband & Wife" leads
    suitable for Sly Broadcasting voicemail drops.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    sb = create_client(url, key)
    
    # Pull all leads to extract priority segments from raw_research
    print("🚀 EXPORT: Fetching leads for quality audit...")
    res = sb.table('contacts_master').select('id,company_name,phone,raw_research').limit(5000).execute()
    
    priority_leads = []
    
    for r in res.data:
        rr = r.get('raw_research')
        if not rr: continue
        if isinstance(rr, str):
            try: rr = json.loads(rr)
            except: continue
        
        # Check for priority flag
        if rr.get('is_priority_owner'):
            phone = r.get('phone', '').strip()
            # Basic Sly phone validation (needs to be non-empty)
            if phone:
                priority_leads.append({
                    "Business Name": r.get('company_name'),
                    "Phone": phone,
                    "Priority": "Husband & Wife Team",
                    "Source": r.get('id')
                })
    
    if not priority_leads:
        print("⚠️ No priority leads found yet. Identification strike may still be in progress.")
        return
        
    filename = f"exports/sly_priority_leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    os.makedirs("exports", exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=priority_leads[0].keys())
        writer.writeheader()
        writer.writerows(priority_leads)
        
    print(f"✅ EXPORT COMPLETE: {len(priority_leads)} leads saved to {filename}")
    return filename

if __name__ == "__main__":
    generate_sly_export()
