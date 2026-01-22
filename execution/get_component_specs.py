import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    sys.exit(1)

client = create_client(url, key)

# Get specs for Advanced Neural Prospecting
try:
    res = client.table("buildable_components").select("*").ilike("component_name", "%Automated Reporting%").execute()
    data = res.data or []
    if data:
        item = data[0]
        print(f"COMPONENT: {item.get('component_name')}")
        print(f"DESCRIPTION: {item.get('description')}")
        print(f"DEPENDENCIES: {item.get('dependencies')}")
        print(f"TECH SPECS: {item.get('tech_implementation')}") # Guessing column name
    else:
        print("No component found in DB matching 'Neural Prospecting'")
except Exception as e:
    print(f"Error: {e}")
