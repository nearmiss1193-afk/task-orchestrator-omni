"""Check EXACT schema of leads table."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = create_client(url, key)

print("🔍 PROBING LEADS TABLE SCHEMA:")
print("=" * 60)

# Get one row to see actual columns
result = client.table("leads").select("*").limit(1).execute()

if result.data:
    print("\n📋 ACTUAL COLUMNS FOUND:")
    for col, val in result.data[0].items():
        print(f"  {col}: {type(val).__name__} = {str(val)[:50]}")
else:
    print("Table is empty")

# Now try inserting with different column combos to see what works
print("\n🧪 TESTING INSERTS:")

# Test 1: Try with company_name
try:
    test = client.table("leads").insert({
        'company_name': 'TEST_COMPANY_DELETE_ME',
        'status': 'test',
        'phone': '+13525551234'
    }).execute()
    print("  ✅ company_name + status + phone WORKS")
    # Delete test record
    client.table("leads").delete().eq('company_name', 'TEST_COMPANY_DELETE_ME').execute()
except Exception as e:
    print(f"  ❌ company_name failed: {str(e)[:100]}")

# Test 2: Check if email column exists
try:
    test = client.table("leads").insert({
        'email': 'test@test.com',
        'status': 'test'
    }).execute()
    print("  ✅ email + status WORKS")
    client.table("leads").delete().eq('email', 'test@test.com').execute()
except Exception as e:
    print(f"  ❌ email failed: {str(e)[:100]}")
