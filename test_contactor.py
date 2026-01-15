"""Test contactor query to debug why leads aren't being found"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
print(f"Supabase URL: {url}")
print(f"Key present: {bool(key)}")

sb = create_client(url, key)

# Test the exact query from contactor
print("\n=== Testing Contactor Query ===")

# 1. Audited
leads = sb.table("leads").select("*").eq("status", "audited").limit(5).execute()
print(f"Audited leads: {len(leads.data)}")

# 2. Enriched
leads = sb.table("leads").select("*").eq("status", "enriched").limit(5).execute()
print(f"Enriched leads: {len(leads.data)}")

# 3. New with phone
leads = sb.table("leads").select("*").eq("status", "new").not_.is_("phone", "null").order("created_at", desc=True).limit(5).execute()
print(f"New leads with phone: {len(leads.data)}")

for l in leads.data:
    print(f"  {l.get('company_name')}: phone={l.get('phone')}, email={l.get('email')}")
