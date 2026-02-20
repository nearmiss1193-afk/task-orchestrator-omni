"""
Stop all outreach on manus_jacksonville leads — mark as bad_data.
Only ~60 of 1000 were real businesses.
"""
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

# Count current Jacksonville leads by status
jax = sb.table("contacts_master").select("status", count="exact").eq("lead_source", "manus_jacksonville").execute()
print(f"Total Jacksonville leads: {jax.count}")

# Mark ALL manus_jacksonville leads as bad_data to pull them from outreach queue
result = sb.table("contacts_master").update({
    "status": "bad_data"
}).eq("lead_source", "manus_jacksonville").execute()

print(f"Updated {len(result.data)} Jacksonville leads to status='bad_data'")

# Verify
remaining_new = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "manus_jacksonville").eq("status", "new").execute()
remaining_bad = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "manus_jacksonville").eq("status", "bad_data").execute()
total_new = sb.table("contacts_master").select("*", count="exact").eq("status", "new").execute()

print(f"\nPost-update:")
print(f"  Jacksonville still 'new': {remaining_new.count}")
print(f"  Jacksonville 'bad_data':  {remaining_bad.count}")
print(f"  Total pipeline (new):     {total_new.count}")
