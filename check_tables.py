"""Check ALL tables in Supabase to find where leads are going."""
import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = create_client(url, key)

print("🔍 CHECKING SUPABASE TABLES:")
print("=" * 60)

# Check leads table
print("\n📋 LEADS TABLE (last 5):")
try:
    result = client.table("leads").select("id,company_name,status,phone,last_called").order("id", desc=True).limit(5).execute()
    for lead in result.data:
        print(f"  {lead}")
except Exception as e:
    print(f"  Error: {e}")

# Check system_logs table  
print("\n📋 SYSTEM_LOGS TABLE (last 5):")
try:
    result = client.table("system_logs").select("*").order("id", desc=True).limit(5).execute()
    for log in result.data:
        print(f"  {log.get('level')} - {log.get('message', '')[:50]}")
except Exception as e:
    print(f"  Error: {e}")

# Check if there's a campaigns table
print("\n📋 CAMPAIGNS TABLE:")
try:
    result = client.table("campaigns").select("*").limit(3).execute()
    print(f"  Found {len(result.data)} campaigns")
    for c in result.data:
        print(f"  {c}")
except Exception as e:
    print(f"  Not found or error: {e}")
