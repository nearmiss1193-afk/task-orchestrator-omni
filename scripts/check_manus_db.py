from modules.database.supabase_client import get_supabase
import json

supabase = get_supabase()
if supabase:
    res = supabase.table("contacts_master").select("*").eq("source", "manus").execute()
    print(f"Found {len(res.data)} Manus leads.")
    for lead in res.data:
        print(f"ID: {lead['id']} | Company: {lead['company_name']} | Status: {lead['status']}")
else:
    print("Failed to initialize Supabase.")
