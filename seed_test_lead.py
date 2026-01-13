"""
EMERGENCY SEED: Add test leads to get system operational
"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

sb = create_client(url, key)

# Test leads with audit links ready
test_leads = [
    {
        "company_name": "Test HVAC Co",
        "email": "owner@aiserviceco.com",  # Send to owner for testing
        "phone": "+13527585336",
        "industry": "hvac",
        "audit_link": "https://prod.analyzemy.business/#/share/report/test123",
        "status": "ready"
    }
]

print("Seeding test leads...")
for lead in test_leads:
    try:
        result = sb.table('leads').insert(lead).execute()
        print(f"  Added: {lead['company_name']}")
    except Exception as e:
        print(f"  Error: {e}")

print("Done!")
