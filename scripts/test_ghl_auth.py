"""Quick test: create a single GHL contact to verify auth works"""
import os, requests
from dotenv import load_dotenv
load_dotenv()

GHL_API_TOKEN = os.environ.get('GHL_AGENCY_API_TOKEN') or os.environ.get('GHL_API_TOKEN', '')
GHL_LOCATION_ID = "uFYcZA7Zk6EcBze5B4oH"

print(f"Token: {GHL_API_TOKEN[:20]}...")
print(f"Location: {GHL_LOCATION_ID}")

# Test 1: GET contacts (should work per existing script)
headers = {
    'Authorization': f'Bearer {GHL_API_TOKEN}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}

print("\n--- Test 1: GET contacts (existing working pattern) ---")
r1 = requests.get(
    f"https://services.leadconnectorhq.com/contacts/?locationId={GHL_LOCATION_ID}&limit=1",
    headers=headers, timeout=15
)
print(f"  Status: {r1.status_code}")
print(f"  Response: {r1.text[:200]}")

# Test 2: POST create contact (what enrichment needs)
print("\n--- Test 2: POST create contact ---")
test_contact = {
    "locationId": GHL_LOCATION_ID,
    "firstName": "TestEnrich",
    "lastName": "DeleteMe",
    "email": f"test-enrich-{os.urandom(4).hex()}@test.com",
    "source": "API Test",
    "tags": ["test-delete"]
}

r2 = requests.post(
    "https://services.leadconnectorhq.com/contacts/",
    headers=headers, json=test_contact, timeout=15
)
print(f"  Status: {r2.status_code}")
print(f"  Response: {r2.text[:300]}")

if r2.status_code in [200, 201]:
    new_id = r2.json().get('contact', {}).get('id', '')
    print(f"  ✅ Created contact: {new_id}")
    
    # Clean up test contact
    r3 = requests.delete(
        f"https://services.leadconnectorhq.com/contacts/{new_id}",
        headers=headers, timeout=15
    )
    print(f"  Cleanup: {r3.status_code}")
else:
    print("  ❌ Failed to create contact")
    print(f"  Full response: {r2.text}")
