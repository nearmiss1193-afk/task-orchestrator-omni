import os, sys
sys.path.insert(0,'.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

s = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

r = s.table("contacts_master").select("company_name,email,website_url,status,source").ilike("source","web_search_%").execute()
print("NEW WEB SEARCH LEADS:", len(r.data))
with_email = [x for x in r.data if x.get("email")]
print("  With email:", len(with_email))
print("  Website only:", len(r.data) - len(with_email))
print()
for lead in r.data:
    em = lead.get("email") or "NO-EMAIL"
    cn = lead.get("company_name", "?")[:35]
    print(f"  {cn} | {em} | {lead.get('status')}")

total_new = s.table("contacts_master").select("id", count="exact").eq("status","new").execute()
print(f"\nTOTAL status=new: {total_new.count}")
total_all = s.table("contacts_master").select("id", count="exact").execute()
print(f"TOTAL in DB: {total_all.count}")
