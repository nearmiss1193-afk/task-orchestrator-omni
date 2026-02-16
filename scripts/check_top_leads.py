from modules.database.supabase_client import get_supabase
import json

def check_leads():
    supabase = get_supabase()
    targets = ['Precaj', 'Aesthetic', 'Asian Kitchen']
    
    print("--- LEAD STATUS ---")
    for name in targets:
        r = supabase.table('contacts_master').select('*').ilike('company_name', f'%{name}%').execute()
        for d in r.data:
            print(f"Company: {d['company_name']}")
            print(f"  Status: {d['status']}")
            print(f"  Email: {d['email']}")
            print(f"  Phone: {d['phone']}")
            
            # Check touches
            t = supabase.table('outbound_touches').select('*').eq('contact_id', d['id']).execute()
            print(f"  Touches: {len(t.data)}")
            for touch in t.data:
                print(f"    - {touch['channel']} | {touch['status']} | {touch['ts']}")
            print("-" * 30)

if __name__ == "__main__":
    check_leads()
