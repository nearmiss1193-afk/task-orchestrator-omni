"""Lead status distribution - count only"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Get all leads with just status field, paginated
print("=== LEAD STATUS DISTRIBUTION ===")
all_statuses = []
offset = 0
while True:
    r = sb.table("contacts_master").select("status").range(offset, offset + 999).execute()
    if not r.data:
        break
    all_statuses.extend(x.get("status", "NULL") for x in r.data)
    if len(r.data) < 1000:
        break
    offset += 1000

from collections import Counter
for status, count in Counter(all_statuses).most_common():
    print(f"  {status}: {count}")
print(f"  TOTAL: {len(all_statuses)}")

# Check specific contactable counts
print("\n=== CONTACTABLE LEADS ===")
for s in ["new", "research_done"]:
    c = sb.table("contacts_master").select("id", count="exact").eq("status", s).limit(1).execute()
    print(f"  {s}: {c.count}")

# Count leads with email by status
print("\n=== LEADS WITH EMAIL BY STATUS ===")
for status in Counter(all_statuses).keys():
    c = sb.table("contacts_master").select("id", count="exact").eq("status", status).neq("email", "").limit(1).execute()
    print(f"  {status} + email: {c.count}")
