"""
Investigate the 190 no_contact_info leads — schema-safe version
"""
import os, json
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "")
sb = create_client(url, key)

print("=" * 60)
print("NO-CONTACT LEADS INVESTIGATION")
print("=" * 60)

# 1. Status breakdown
r = sb.table("contacts_master").select("status").execute()
statuses = {}
for row in (r.data or []):
    s = row.get('status', 'unknown')
    statuses[s] = statuses.get(s, 0) + 1
print(f"\n1. STATUS BREAKDOWN:")
for s, c in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f"   {s}: {c}")

# 2. Sample no_contact_info leads — get ALL columns to see schema
r = sb.table("contacts_master").select("*").eq("status", "no_contact_info").limit(3).execute()
if r.data:
    print(f"\n2. SCHEMA (all columns from first lead):")
    for k in sorted(r.data[0].keys()):
        print(f"   {k}")
    
    print(f"\n3. SAMPLE LEADS ({len(r.data)} shown):")
    for i, lead in enumerate(r.data):
        print(f"\n   --- Lead {i+1} ---")
        for k, v in sorted(lead.items()):
            if v is not None and v != '' and v != [] and v != {}:
                val = str(v)[:100]
                print(f"   {k}: {val}")

# 3. Check new leads too
r3 = sb.table("contacts_master").select("*").eq("status", "new").limit(3).execute()
if r3.data:
    print(f"\n4. SAMPLE 'NEW' LEADS ({len(r3.data)} shown):")
    for i, lead in enumerate(r3.data):
        print(f"\n   --- New Lead {i+1} ---")
        for k, v in sorted(lead.items()):
            if v is not None and v != '' and v != [] and v != {}:
                val = str(v)[:100]
                print(f"   {k}: {val}")

# 4. Interested lead
r4 = sb.table("contacts_master").select("*").eq("status", "interested").execute()
if r4.data:
    print(f"\n5. INTERESTED LEAD:")
    for k, v in sorted(r4.data[0].items()):
        if v is not None and v != '' and v != [] and v != {}:
            val = str(v)[:100]
            print(f"   {k}: {val}")

print(f"\n{'=' * 60}")
