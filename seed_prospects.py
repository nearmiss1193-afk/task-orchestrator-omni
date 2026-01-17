"""
Seed prospect targets for autonomous prospecting
"""
import requests

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

headers = {
    'apikey': SUPABASE_KEY, 
    'Authorization': f'Bearer {SUPABASE_KEY}', 
    'Content-Type': 'application/json', 
    'Prefer': 'return=minimal'
}

prospects = [
    {'industry': 'hvac', 'location': 'Tampa FL', 'status': 'pending'},
    {'industry': 'plumbing', 'location': 'Orlando FL', 'status': 'pending'},
    {'industry': 'roofing', 'location': 'Jacksonville FL', 'status': 'pending'},
    {'industry': 'landscaping', 'location': 'Miami FL', 'status': 'pending'},
    {'industry': 'electrician', 'location': 'Fort Myers FL', 'status': 'pending'},
    {'industry': 'auto detailing', 'location': 'Clearwater FL', 'status': 'pending'},
    {'industry': 'cleaning services', 'location': 'Sarasota FL', 'status': 'pending'},
    {'industry': 'pest control', 'location': 'St Petersburg FL', 'status': 'pending'},
    {'industry': 'pool service', 'location': 'Naples FL', 'status': 'pending'},
    {'industry': 'lawn care', 'location': 'Gainesville FL', 'status': 'pending'},
]

print("🚀 Seeding prospect targets...")
added = 0
for p in prospects:
    r = requests.post(f'{SUPABASE_URL}/rest/v1/prospect_targets', headers=headers, json=p, timeout=10)
    status = "✅" if r.status_code in [200, 201] else f"❌ {r.status_code}"
    print(f"  {p['industry']} in {p['location']}: {status}")
    if r.status_code in [200, 201]:
        added += 1

print(f"\n✅ Added {added}/{len(prospects)} prospect targets")
print("Next prospecting run will generate AI audits for these industries!")
