import modal
from deploy import image, VAULT

app = modal.App("lead-audit")

@app.function(image=image, secrets=[VAULT])
def audit_leads():
    from modules.database.supabase_client import get_supabase
    import json
    
    supabase = get_supabase()
    targets = ['Precaj', 'Asian Kitchen']
    
    results = []
    for name in targets:
        r = supabase.table('contacts_master').select('*').ilike('company_name', f'%{name}%').execute()
        for d in r.data:
            lead_info = {
                "company": d['company_name'],
                "status": d['status'],
                "email": d['email'],
                "touches": []
            }
            # Check touches
            t = supabase.table('outbound_touches').select('*').eq('contact_id', d['id']).execute()
            for touch in t.data:
                lead_info["touches"].append({
                    "channel": touch['channel'],
                    "status": touch['status'],
                    "ts": touch['ts']
                })
            results.append(lead_info)
    
    return results

if __name__ == "__main__":
    with app.run():
        res = audit_leads.remote()
        print(json.dumps(res, indent=2))
