from modules.database.supabase_client import get_supabase
import json

supabase = get_supabase()
if supabase:
    companies = ["Downtown Air and Heat", "Uptown Oaks", "Gary Munson Heating and Air Conditioning"]
    for company in companies:
        res = supabase.table("contacts_master").select("*").ilike("company_name", f"%{company}%").execute()
        print(f"Searched '{company}': Found {len(res.data)} matches.")
        for lead in res.data:
            print(f"  ID: {lead['id']} | Status: {lead['status']} | Source: {lead['source']}")
else:
    print("Failed to initialize Supabase.")
