"""Analyze leads and find ones with valid phones for calling"""
from supabase import create_client
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

print("=" * 70)
print("LEAD ANALYSIS - FINDING CALLABLE LEADS")
print("=" * 70)

# Get leads that are new or processing_email
result = client.table('leads').select('*').in_('status', ['new', 'processing_email']).limit(20).execute()

valid_leads = []
invalid_leads = []

for lead in result.data:
    company = lead.get('company_name', 'N/A')
    
    # Extract phone from multiple possible locations
    phone = lead.get('phone', '')
    agent_research = lead.get('agent_research', {})
    if isinstance(agent_research, str):
        try:
            agent_research = json.loads(agent_research)
        except:
            agent_research = {}
    
    research_phone = agent_research.get('phone', '') if agent_research else ''
    actual_phone = phone or research_phone or ''
    
    # Validate
    if actual_phone:
        cleaned = re.sub(r'\D', '', str(actual_phone))
        # Check if 555 is in the exchange (middle 3 digits of 10-digit number)
        has_555 = False
        if len(cleaned) >= 10:
            exchange = cleaned[-7:-4]  # Extract exchange
            has_555 = exchange == '555'
        
        if len(cleaned) >= 10 and not has_555:
            valid_leads.append({
                'id': lead.get('id'),
                'company': company,
                'phone': cleaned,
                'email': lead.get('email') or agent_research.get('email', 'N/A')
            })
        else:
            reason = '555 exchange' if has_555 else 'too short'
            invalid_leads.append({'company': company, 'phone': actual_phone, 'reason': reason})
    else:
        invalid_leads.append({'company': company, 'phone': 'MISSING', 'reason': 'no phone'})

print("\n=== VALID LEADS (CALLABLE) ===")
for lead in valid_leads[:10]:
    print(f"  ID {lead['id']}: {lead['company'][:30]:30} | +1{lead['phone'][-10:]} | {lead['email'][:25]}")

print(f"\n  Total valid: {len(valid_leads)}")

print("\n=== INVALID LEADS (SKIPPED) ===")
for lead in invalid_leads[:10]:
    print(f"  {lead['company'][:30]:30} | {lead['phone']:15} | {lead['reason']}")

print(f"\n  Total invalid: {len(invalid_leads)}")

# Check if the problem is the ORDER of leads (first 5 are invalid)
print("\n=== FIRST 5 LEADS BY ORDER (what cloud_multi_touch sees) ===")
first5 = client.table('leads').select('*').in_('status', ['new', 'processing_email']).limit(5).execute()
for lead in first5.data:
    company = lead.get('company_name', 'N/A')
    phone = lead.get('phone', '')
    agent_research = lead.get('agent_research', {})
    if isinstance(agent_research, str):
        try:
            agent_research = json.loads(agent_research)
        except:
            agent_research = {}
    research_phone = agent_research.get('phone', '') if agent_research else ''
    actual_phone = phone or research_phone or 'NONE'
    
    cleaned = re.sub(r'\D', '', str(actual_phone)) if actual_phone != 'NONE' else ''
    exchange = cleaned[-7:-4] if len(cleaned) >= 7 else 'N/A'
    
    print(f"  {company[:30]:30} | {actual_phone:15} | exchange: {exchange}")

print("\n" + "=" * 70)
