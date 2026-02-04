"""Generate 10 fresh leads for approval"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

print('=== GENERATING 10 FRESH LEADS ===')

APOLLO_KEY = os.environ.get('APOLLO_API_KEY', '')
if not APOLLO_KEY:
    print('ERROR: APOLLO_API_KEY not found')
    exit(1)

payload = {
    'api_key': APOLLO_KEY,
    'q_organization_keyword': 'HVAC air conditioning heating',
    'organization_locations': ['Florida, United States'],
    'organization_num_employees_ranges': ['1,10', '11,20', '21,50'],
    'page': 1,
    'per_page': 10
}

r = requests.post('https://api.apollo.io/v1/mixed_people/search', json=payload)
data = r.json()
leads = data.get('people', [])
print(f'Found {len(leads)} leads')

previews = []
for l in leads[:10]:
    preview = {
        'name': l.get('name', 'N/A'),
        'company': l.get('organization', {}).get('name', 'N/A'),
        'title': l.get('title', 'N/A'),
        'email': l.get('email', 'N/A'),
        'city': l.get('city', 'N/A'),
        'state': l.get('state', 'N/A')
    }
    previews.append(preview)
    print(f"  - {preview['name']} @ {preview['company']} ({preview['city']}, {preview['state']})")

with open('leads_for_approval.json', 'w') as f:
    json.dump({'leads': previews, 'status': 'PENDING_APPROVAL', 'count': len(previews)}, f, indent=2)

print(f'\n=== {len(previews)} LEADS QUEUED FOR APPROVAL ===')
print('File: leads_for_approval.json')
