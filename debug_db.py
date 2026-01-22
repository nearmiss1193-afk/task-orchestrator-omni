import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:10]}...")

supabase = create_client(url, key)

try:
    # Try simple read
    print("Reading...")
    res = supabase.table("contacts_master").select("count", count="exact").limit(1).execute()
    print(f"Read Success. Count: {res.count}")
    
    # Try insert
    print("Inserting...")
    test_lead = {"ghl_contact_id": "debug_123", "email": "debug@example.com", "status": "new"}
    supabase.table("contacts_master").upsert(test_lead, on_conflict="ghl_contact_id").execute()
    print("Insert Success.")
    
    # Clean
    supabase.table("contacts_master").delete().eq("ghl_contact_id", "debug_123").execute()
    print("Cleanup Success.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'details'):
       print(f"Details: {e.details}")
    if hasattr(e, 'message'):
       print(f"Message: {e.message}")
