"""Test Apollo enrichment"""
from hunter_apollo_integration import find_person_by_company, find_decision_makers
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("APOLLO.IO ENRICHMENT TEST")
print("=" * 60)

apollo_key = os.getenv("APOLLO_API_KEY")
print(f"Apollo API Key: {'SET (' + apollo_key[:10] + '...)' if apollo_key else 'NOT SET'}")

# Test 1: Find HVAC decision makers
print("\n=== Test 1: Find HVAC company decision maker ===")
people = find_person_by_company("Preferred Air Solutions Tampa", "Owner", limit=3)
for p in people:
    if "name" in p:
        print(f"  FOUND: {p.get('name')} | {p.get('title')} | {p.get('email')} | {p.get('phone')}")
    else:
        print(f"  Result: {p}")

# Test 2: Find decision makers with multiple titles
print("\n=== Test 2: Find decision makers (CEO/Owner/President) ===")
dm = find_decision_makers("Air Zero HVAC Orlando")
for p in dm[:5]:
    print(f"  {p.get('name')} | {p.get('title')} | {p.get('email')} | {p.get('phone')}")

print("\n" + "=" * 60)
