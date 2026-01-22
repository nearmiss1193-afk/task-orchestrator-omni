import sys
import os
sys.path.append(os.getcwd())
from execution.alf_matcher import ALFMatcher
import uuid

def test_alf_flow():
    matcher = ALFMatcher()
    
    if not matcher.db_connected:
        print("❌ DB Not Connected")
        return

    print("✅ DB Connected. Attempting Referral Creation...")
    
    # Create test referral
    test_id = str(uuid.uuid4())[:8]
    res = matcher.create_referral(
        family_contact=f"Test Family {test_id}",
        family_phone="555-0100",
        senior_name=f"Grandpa Test {test_id}",
        care_level="assisted",
        budget_min=3000,
        budget_max=5000,
        preferred_city="Orlando"
    )
    
    if res.get("success"):
        ref = res.get("referral")
        print(f"✅ Referral Created! ID: {ref.get('id')}")
        print(f"   Senior: {ref.get('senior_name')}")
        print(f"   Status: {ref.get('status')}")
    else:
        print(f"❌ Creation Failed: {res}")

if __name__ == "__main__":
    test_alf_flow()
