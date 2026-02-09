"""Check customer_memory table structure and data"""
import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing Supabase credentials")
    exit(1)

sb = create_client(url, key)

print("=== CUSTOMER MEMORY - ALL ENTRIES ===\n")
result = sb.table("customer_memory").select("*").execute()

if result.data:
    for entry in result.data:
        print(f"Phone: {entry.get('phone_number')}")
        print(f"customer_name field: {entry.get('customer_name')}")
        print(f"email: {entry.get('email')}")
        ctx = entry.get('context_summary')
        print(f"context_summary TYPE: {type(ctx)}")
        print(f"context_summary VALUE: {json.dumps(ctx, indent=2) if isinstance(ctx, dict) else ctx}")
        if isinstance(ctx, dict):
            print(f"  -> contact_name inside: {ctx.get('contact_name')}")
        print(f"updated_at: {entry.get('updated_at')}")
        print("-" * 50)
else:
    print("No customer_memory entries found")

# Check for Michael specifically
print("\n\n=== SEARCHING FOR MICHAEL ===")
result2 = sb.table("customer_memory").select("*").ilike("context_summary", "%michael%").execute()
if result2.data:
    for e in result2.data:
        print(f"Found: Phone {e['phone_number']}, context_summary: {e['context_summary']}")
else:
    # Try customer_name field
    result3 = sb.table("customer_memory").select("*").ilike("customer_name", "%michael%").execute()
    if result3.data:
        for e in result3.data:
            print(f"Found in customer_name: Phone {e['phone_number']}, customer_name: {e['customer_name']}")
    else:
        print("'Michael' not found in any customer_memory field")

# Check what +1267... looks like
print("\n\n=== CHECK DAN'S PHONE FORMAT ===")
result4 = sb.table("customer_memory").select("*").like("phone_number", "%267%").execute()
if result4.data:
    for e in result4.data:
        print(f"Phone format: {e['phone_number']}")
