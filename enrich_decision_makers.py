"""
DECISION MAKER ENRICHMENT - Using Hunter.io + Apollo.io
Enriches company leads with owner/decision maker direct contact info
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')

def enrich_with_hunter(company_name, domain=None):
    """
    Use Hunter.io to find email addresses for a company
    Returns: List of emails with names and titles
    """
    if not domain:
        # Try to guess domain from company name
        domain = company_name.lower().replace(' ', '').replace('&', 'and') + '.com'
    
    try:
        url = f"https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            emails = data.get('data', {}).get('emails', [])
            
            # Filter for decision makers (owner, CEO, president, founder)
            decision_makers = []
            for email in emails:
                position = email.get('position', '').lower()
                if any(title in position for title in ['owner', 'ceo', 'president', 'founder', 'director']):
                    decision_makers.append({
                        'name': f"{email.get('first_name', '')} {email.get('last_name', '')}".strip(),
                        'email': email.get('value'),
                        'title': email.get('position'),
                        'confidence': email.get('confidence'),
                        'source': 'hunter.io'
                    })
            
            return decision_makers
    except Exception as e:
        print(f"Hunter.io error: {e}")
        return []

def enrich_with_apollo(company_name, domain=None):
    """
    Use Apollo.io to find decision maker contact info
    Returns: List of contacts with phone + email
    """
    try:
        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': APOLLO_API_KEY
        }
        
        # Search for decision makers at this company
        payload = {
            "q_organization_name": company_name,
            "person_titles": ["owner", "ceo", "president", "founder", "managing director"],
            "page": 1,
            "per_page": 5
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            people = data.get('people', [])
            
            decision_makers = []
            for person in people:
                contact = {
                    'name': person.get('name'),
                    'email': person.get('email'),
                    'phone': person.get('phone_numbers', [{}])[0].get('sanitized_number') if person.get('phone_numbers') else None,
                    'title': person.get('title'),
                    'linkedin': person.get('linkedin_url'),
                    'source': 'apollo.io'
                }
                
                # Only include if we have at least email or phone
                if contact['email'] or contact['phone']:
                    decision_makers.append(contact)
            
            return decision_makers
    except Exception as e:
        print(f"Apollo.io error: {e}")
        return []

def enrich_lead(company_name, domain=None, phone=None):
    """
    Main enrichment function - tries both Hunter and Apollo
    Returns best decision maker contact found
    """
    print(f"\n🔍 Enriching: {company_name}")
    
    all_contacts = []
    
    # Try Hunter.io first (faster, email-focused)
    hunter_contacts = enrich_with_hunter(company_name, domain)
    if hunter_contacts:
        print(f"  ✅ Hunter.io: Found {len(hunter_contacts)} decision makers")
        all_contacts.extend(hunter_contacts)
    
    # Try Apollo.io (has phone numbers)
    apollo_contacts = enrich_with_apollo(company_name, domain)
    if apollo_contacts:
        print(f"  ✅ Apollo.io: Found {len(apollo_contacts)} decision makers")
        all_contacts.extend(apollo_contacts)
    
    if not all_contacts:
        print(f"  ❌ No decision makers found")
        return None
    
    # Prioritize contacts with both email AND phone
    best_contact = None
    for contact in all_contacts:
        if contact.get('email') and contact.get('phone'):
            best_contact = contact
            break
    
    # If no contact has both, take the first one with either
    if not best_contact:
        best_contact = all_contacts[0]
    
    print(f"  🎯 Best contact: {best_contact.get('name')} ({best_contact.get('title')})")
    print(f"     Email: {best_contact.get('email')}")
    print(f"     Phone: {best_contact.get('phone')}")
    
    return best_contact

# Test function
if __name__ == '__main__':
    # Test with a sample company
    test_company = "JW Plumbing Heating Air"
    result = enrich_lead(test_company)
    
    if result:
        print(f"\n✅ SUCCESS!")
        print(f"Name: {result.get('name')}")
        print(f"Email: {result.get('email')}")
        print(f"Phone: {result.get('phone')}")
        print(f"Title: {result.get('title')}")
        print(f"Source: {result.get('source')}")
    else:
        print("\n❌ No decision maker found")
