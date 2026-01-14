"""Test the exact prospecting flow locally"""
from dotenv import load_dotenv
load_dotenv('backups/empire_backup_20260108_182239/source/.env')
import os
import requests

# Use the same env vars as Railway
APOLLO_KEY = os.environ.get("APOLLO_API_KEY")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

print(f"Apollo Key: {APOLLO_KEY[:20] if APOLLO_KEY else 'MISSING'}...")
print(f"Supabase URL: {SUPABASE_URL}")

# Step 1: Test Apollo
print("\n--- Apollo Search ---")
r = requests.post(
    "https://api.apollo.io/v1/organizations/search",
    headers={"Content-Type": "application/json", "X-Api-Key": APOLLO_KEY},
    json={
        "q_keywords": "HVAC contractor",
        "organization_locations": ["Florida"],
        "organization_num_employees_ranges": ["1,50"],
        "per_page": 2
    },
    timeout=30
)
print(f"Status: {r.status_code}")

if r.ok:
    companies = r.json().get("organizations", [])
    print(f"Found {len(companies)} companies")
    
    if companies:
        company = companies[0]
        print(f"First: {company.get('name')}")
        
        # Step 2: Try to save to Supabase
        lead = {
            "company_name": company.get("name"),
            "website_url": company.get("website_url"),
            "phone": company.get("phone"),
            "city": company.get("city"),
            "state": company.get("state"),
            "status": "new"
        }
        print(f"\n--- Saving to Supabase ---")
        print(f"Lead data: {lead}")
        
        save_r = requests.post(
            f"{SUPABASE_URL}/rest/v1/leads",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json=lead,
            timeout=15
        )
        print(f"Save status: {save_r.status_code}")
        if not save_r.ok:
            print(f"Error: {save_r.text}")
        else:
            print("✅ Lead saved successfully!")
else:
    print(f"Apollo Error: {r.text}")
