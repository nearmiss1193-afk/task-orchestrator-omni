import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

total = sb.table("contacts_master").select("*", count="exact").limit(0).execute()
jax = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "manus_jacksonville").limit(0).execute()
new_leads = sb.table("contacts_master").select("*", count="exact").eq("status", "new").limit(0).execute()

with open("import_results.txt", "w") as f:
    f.write(f"Total contacts_master: {total.count}\n")
    f.write(f"Jacksonville leads:    {jax.count}\n")
    f.write(f"Contactable (new):     {new_leads.count}\n")
    
    # Sample a few Jacksonville leads
    samples = sb.table("contacts_master").select("company_name,email,phone,niche,full_name,status").eq("lead_source", "manus_jacksonville").limit(5).execute()
    f.write(f"\nSample Jacksonville leads:\n")
    for s in samples.data:
        f.write(f"  {s['company_name']} | {s['email']} | {s['phone']} | {s['niche']} | {s['full_name']}\n")

    # Category breakdown
    all_jax = sb.table("contacts_master").select("niche").eq("lead_source", "manus_jacksonville").execute()
    from collections import Counter
    cats = Counter(r["niche"] for r in all_jax.data)
    f.write(f"\nBy category:\n")
    for cat, count in cats.most_common():
        f.write(f"  {cat}: {count}\n")

print("Results written to import_results.txt")
