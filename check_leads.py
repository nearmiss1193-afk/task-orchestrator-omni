"""Check recent leads in Supabase."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = create_client(url, key)

print("🔍 RECENT LEADS IN SUPABASE:")
print("-" * 60)

try:
    result = client.table("leads").select("*").order("id", desc=True).limit(10).execute()
    
    if result.data:
        for lead in result.data:
            print(f"ID: {lead.get('id')}")
            print(f"  Company: {lead.get('company_name', 'N/A')}")
            print(f"  Status: {lead.get('status', 'N/A')}")
            print(f"  Phone: {lead.get('phone', 'N/A')}")
            print(f"  Last Called: {lead.get('last_called', 'N/A')}")
            print("-" * 40)
    else:
        print("No leads found in table!")
        
except Exception as e:
    print(f"Error: {e}")
