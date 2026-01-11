"""
West Coast Prospector - Automated prospect building for CA, OR, WA, HI
Runs during off-hours to build pipeline
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

STATE_CONFIGS = {
    "CA": {
        "name": "California",
        "major_cities": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento"],
        "target_count": 500
    },
    "OR": {
        "name": "Oregon",
        "major_cities": ["Portland", "Eugene", "Salem", "Bend"],
        "target_count": 200
    },
    "WA": {
        "name": "Washington",
        "major_cities": ["Seattle", "Spokane", "Tacoma", "Vancouver"],
        "target_count": 200
    },
    "HI": {
        "name": "Hawaii",
        "major_cities": ["Honolulu", "Hilo", "Kailua"],
        "target_count": 100
    }
}

def search_hvac_companies(city, state, limit=50):
    """
    Search for HVAC companies in a specific city/state
    Uses Google Places API or similar
    """
    # This would integrate with Google Places API
    # For now, returning mock data structure
    
    companies = []
    
    # Example structure - would be populated from API
    company = {
        "name": f"Example HVAC {city}",
        "city": city,
        "state": state,
        "phone": "+1-555-0100",
        "website": f"https://example-hvac-{city.lower()}.com",
        "address": f"123 Main St, {city}, {state}",
        "employee_count": 25,
        "source": "google_places",
        "acquired_at": datetime.now().isoformat()
    }
    
    companies.append(company)
    
    return companies

def save_prospect_to_database(company):
    """Save prospect to Supabase"""
    try:
        # Check if already exists
        existing = supabase.table("leads").select("*").eq("phone", company["phone"]).execute()
        
        if existing.data:
            print(f"  ⚠️  Already exists: {company['name']}")
            return False
        
        # Insert new prospect
        data = {
            "business_name": company["name"],
            "city": company["city"],
            "state": company["state"],
            "phone": company["phone"],
            "website": company.get("website"),
            "address": company.get("address"),
            "employee_count": company.get("employee_count"),
            "source": company.get("source", "prospector"),
            "status": "new",
            "needs_dm_research": True,  # MANDATORY: Flag for decision maker research
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("leads").insert(data).execute()
        print(f"  ✓ Saved: {company['name']}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error saving {company['name']}: {e}")
        return False

def build_prospects(state, target_count=None):
    """
    Build prospect list for a specific state
    
    Args:
        state: State code (CA, OR, WA, HI)
        target_count: Number of prospects to acquire (default from config)
    """
    if state not in STATE_CONFIGS:
        print(f"Invalid state: {state}")
        return
    
    config = STATE_CONFIGS[state]
    target = target_count or config["target_count"]
    
    print(f"\n{'='*70}")
    print(f"BUILDING PROSPECTS: {config['name']} ({state})")
    print(f"Target: {target} companies")
    print(f"{'='*70}\n")
    
    total_saved = 0
    
    for city in config["major_cities"]:
        print(f"\nSearching: {city}, {state}")
        
        # Search for HVAC companies
        companies = search_hvac_companies(city, state, limit=50)
        
        print(f"Found {len(companies)} companies")
        
        # Save to database
        for company in companies:
            if save_prospect_to_database(company):
                total_saved += 1
            
            if total_saved >= target:
                break
        
        if total_saved >= target:
            break
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: Saved {total_saved} new prospects for {state}")
    print(f"{'='*70}\n")
    
    return total_saved

def build_all_west_coast_prospects():
    """Build prospects for all West Coast + Hawaii states"""
    print("\n" + "="*70)
    print("WEST COAST PROSPECTOR - FULL RUN")
    print("="*70)
    
    total_all_states = 0
    
    for state in ["CA", "OR", "WA", "HI"]:
        count = build_prospects(state)
        total_all_states += count
    
    print(f"\n{'='*70}")
    print(f"TOTAL PROSPECTS ACQUIRED: {total_all_states}")
    print(f"{'='*70}\n")
    
    return total_all_states

if __name__ == "__main__":
    # Run for all states
    build_all_west_coast_prospects()
