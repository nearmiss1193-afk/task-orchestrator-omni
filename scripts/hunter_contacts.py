"""Hunter.io Contact Finder - Find decision-makers for email personalization"""
import requests
import json

HUNTER_API_KEY = 'db66f8de44346b2a5a9fe8d1cb09b58f4aaebfe7'

# The 10 businesses we need contacts for
businesses = [
    {'name': 'Lakeland Roofing Company', 'domain': 'lakelandroofing.com'},
    {'name': 'All Pro Roofing', 'domain': 'allproroofingfl.com'},
    {'name': 'Precision Roofing Lakeland', 'domain': 'precisionroofinglakeland.com'},
    {'name': 'Scotts Air Conditioning', 'domain': 'scottsair.com'},
    {'name': 'Air Pros USA', 'domain': 'airprosusa.com'},
    {'name': 'Lakeland Air Conditioning', 'domain': 'lakelandairconditioning.com'},
    {'name': 'Viper Auto Care', 'domain': 'viperautocare.com'},
    {'name': 'Honest 1 Auto Care Lakeland', 'domain': 'honest1lakeland.com'},
    {'name': 'Premium Auto Repair', 'domain': 'premiumautorepairlakeland.com'},
    {'name': 'ABC Plumbing Lakeland', 'domain': 'abcplumbinglakeland.com'},
]

results = []

print('HUNTER.IO CONTACT SEARCH RESULTS')
print('=' * 60)

for biz in businesses:
    domain = biz['domain']
    url = f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}'
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if 'data' in data and data['data'].get('emails'):
            emails = data['data']['emails']
            first = emails[0]
            first_name = first.get('first_name', '')
            last_name = first.get('last_name', '')
            name = f"{first_name} {last_name}".strip()
            email = first.get('value', '')
            position = first.get('position', '')
            
            result = {
                'business': biz['name'],
                'domain': domain,
                'contact_name': name or 'Unknown',
                'first_name': first_name,
                'email': email,
                'position': position,
                'found': True
            }
            print(f"[FOUND] {biz['name']}: {name} - {email}")
        else:
            result = {
                'business': biz['name'],
                'domain': domain,
                'contact_name': None,
                'first_name': None,
                'email': None,
                'position': None,
                'found': False
            }
            print(f"[NOT FOUND] {biz['name']}: No contacts found")
            
    except Exception as e:
        result = {
            'business': biz['name'],
            'domain': domain,
            'error': str(e),
            'found': False
        }
        print(f"[ERROR] {biz['name']}: {str(e)[:50]}")
    
    results.append(result)

# Save results
with open('hunter_contacts.json', 'w') as f:
    json.dump(results, f, indent=2)

print('=' * 60)
print(f"Results saved to hunter_contacts.json")

# Summary
found = [r for r in results if r.get('found')]
not_found = [r for r in results if not r.get('found')]
print(f"\nSUMMARY: {len(found)} found, {len(not_found)} not found")

if not_found:
    print("\nBUSINESSES NEEDING MANUAL RESEARCH:")
    for r in not_found:
        print(f"  - {r['business']} ({r['domain']})")
