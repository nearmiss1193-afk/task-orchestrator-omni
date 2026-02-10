import os, json
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Get data for the board
samples = s.table("contacts_master").select("full_name,email,ai_strategy,company_name,website_url,status,ghl_contact_id").in_("status", ["new","research_done"]).limit(10).execute()

has_strategy = sum(1 for l in samples.data if l.get('ai_strategy'))
has_scraped = sum(1 for l in samples.data if (l.get('ghl_contact_id') or '').startswith('SCRAPED_'))

print(f"Sample of 10 leads:")
print(f"  With ai_strategy content: {has_strategy}")
print(f"  With SCRAPED_ GHL IDs: {has_scraped}")
print()

# Check all leads for ai_strategy
all_leads = s.table("contacts_master").select("ai_strategy,ghl_contact_id").execute()
strategy_null = sum(1 for l in all_leads.data if not l.get('ai_strategy'))
strategy_set = sum(1 for l in all_leads.data if l.get('ai_strategy'))
scraped_count = sum(1 for l in all_leads.data if (l.get('ghl_contact_id') or '').startswith('SCRAPED_'))
real_ghl = sum(1 for l in all_leads.data if (l.get('ghl_contact_id') or '') and not (l.get('ghl_contact_id') or '').startswith('SCRAPED_'))

print(f"=== ALL LEADS ===")
print(f"Total: {len(all_leads.data)}")
print(f"ai_strategy NULL: {strategy_null}")
print(f"ai_strategy SET: {strategy_set}")
print(f"SCRAPED_ GHL IDs: {scraped_count}")
print(f"Real GHL IDs: {real_ghl}")
print()

# Show what ai_strategy looks like when it exists
for l in all_leads.data:
    if l.get('ai_strategy'):
        print(f"Sample ai_strategy: {l['ai_strategy'][:300]}...")
        break
