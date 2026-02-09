import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Count REAL vs SCRAPED ghl IDs
all_leads = s.table("contacts_master").select("ghl_contact_id,status").execute()
real_ghl = 0
scraped_ghl = 0
no_ghl = 0

for l in all_leads.data:
    gid = l.get('ghl_contact_id', '') or ''
    if gid.startswith('SCRAPED_'):
        scraped_ghl += 1
    elif gid:
        real_ghl += 1
    else:
        no_ghl += 1

print(f"=== GHL ID ANALYSIS ===")
print(f"REAL GHL IDs:    {real_ghl}")
print(f"SCRAPED_ IDs:    {scraped_ghl}")
print(f"No GHL ID:       {no_ghl}")
print(f"Total:           {len(all_leads.data)}")
print()
print(f"SCRAPED_ leads can NOT be sent outreach via GHL webhooks.")
print(f"Only REAL GHL IDs ({real_ghl}) can receive GHL-routed SMS/Email.")
