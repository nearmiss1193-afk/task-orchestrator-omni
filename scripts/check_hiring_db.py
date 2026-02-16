from modules.database.supabase_client import get_supabase
import json

supabase = get_supabase()
if supabase:
    res = supabase.table("contacts_master").select("*").ilike("niche", "%hiring%").execute()
    print(f"Found {len(res.data)} 'hiring' leads.")
    for lead in res.data:
        print(f"ID: {lead['id']} | Company: {lead['company_name']} | Source: {lead['source']} | Niche: {lead['niche']}")
else:
    print("Failed to initialize Supabase.")
