"""Check current new lead count"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Current new leads
r = sb.table("contacts_master").select("id,email,company_name", count="exact").eq("status", "new").limit(10).execute()
print(f"NEW leads: {r.count}")
for x in r.data or []:
    print(f"  {x.get('company_name','?')}: {x.get('email','?')}")

# Count recoverable from each status
for status in ["skipped_no_url", "skipped_no_contact", "outreach_dispatched"]:
    skip = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned', 'notfound']
    leads = sb.table("contacts_master").select("id,email").eq("status", status).execute()
    valid = [l for l in (leads.data or []) if l.get("email") and not any(p in l["email"].lower() for p in skip)]
    print(f"{status}: {len(valid)} recoverable with valid email")

# Re-queue skipped_no_url leads that have email
for status in ["skipped_no_url", "skipped_no_contact", "outreach_dispatched"]:
    skip = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned', 'notfound']
    leads = sb.table("contacts_master").select("id,email,company_name").eq("status", status).execute()
    valid = [l for l in (leads.data or []) if l.get("email") and not any(p in l["email"].lower() for p in skip)]
    for l in valid:
        sb.table("contacts_master").update({"status": "new"}).eq("id", l["id"]).execute()
        print(f"  Re-queued: {l.get('company_name','?')}: {l.get('email','?')}")

# Final count
new_final = sb.table("contacts_master").select("id", count="exact").eq("status", "new").limit(1).execute()
print(f"\nFINAL new leads: {new_final.count}")
