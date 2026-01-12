"""Check why calls are being skipped"""
from supabase import create_client
import os
import re
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

print("=" * 60)
print("CALL SKIP INVESTIGATION")
print("=" * 60)

# 1. Check Vapi credentials
vapi_key = os.getenv("VAPI_PRIVATE_KEY")
vapi_phone = os.getenv("VAPI_PHONE_NUMBER_ID")
print("\n=== VAPI CREDENTIALS ===")
print(f"  VAPI_PRIVATE_KEY: {'SET (' + vapi_key[:10] + '...)' if vapi_key else 'NOT SET!'}")
print(f"  VAPI_PHONE_NUMBER_ID: {vapi_phone if vapi_phone else 'NOT SET!'}")

# 2. Check leads with their phone numbers
print("\n=== LEADS WITH PHONE NUMBERS (new/processing_email) ===")
result = client.table('leads').select('*').in_('status', ['new', 'processing_email']).limit(10).execute()

for lead in result.data:
    company = lead.get('company_name', 'N/A')
    phone = lead.get('phone', '')
    agent_research = lead.get('agent_research', {})
    
    if isinstance(agent_research, str):
        import json
        try:
            agent_research = json.loads(agent_research)
        except:
            agent_research = {}
    
    research_phone = agent_research.get('phone', '') if agent_research else ''
    
    # Get any phone
    actual_phone = phone or research_phone
    
    # Check if valid
    if actual_phone:
        cleaned = re.sub(r'\D', '', str(actual_phone))
        has_555 = '555' in cleaned[3:6] if len(cleaned) >= 6 else False
        valid = len(cleaned) >= 10 and not has_555
        status = 'VALID' if valid else ('555-NUMBER' if has_555 else 'TOO SHORT')
    else:
        status = 'MISSING'
        cleaned = ''
    
    print(f"  {company[:30]:30} | {actual_phone:15} | {status}")

# 3. Count phone validity
print("\n=== PHONE NUMBER ANALYSIS ===")
all_leads = client.table('leads').select('*').in_('status', ['new', 'processing_email']).execute()
valid = 0
invalid_555 = 0
missing = 0
too_short = 0

for lead in all_leads.data:
    import json
    phone = lead.get('phone', '')
    agent_research = lead.get('agent_research', {})
    if isinstance(agent_research, str):
        try:
            agent_research = json.loads(agent_research)
        except:
            agent_research = {}
    research_phone = agent_research.get('phone', '') if agent_research else ''
    actual_phone = phone or research_phone
    
    if not actual_phone:
        missing += 1
    else:
        cleaned = re.sub(r'\D', '', str(actual_phone))
        if len(cleaned) < 10:
            too_short += 1
        elif '555' in cleaned[3:6]:
            invalid_555 += 1
        else:
            valid += 1

print(f"  Valid phones: {valid}")
print(f"  Invalid (555): {invalid_555}")
print(f"  Too short: {too_short}")
print(f"  Missing: {missing}")
print(f"  Total: {valid + invalid_555 + too_short + missing}")

print("\n" + "=" * 60)
