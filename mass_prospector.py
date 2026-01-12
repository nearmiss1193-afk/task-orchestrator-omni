"""
🔥 MASS PROSPECTOR - 300 Leads Per Timezone
============================================
Targets: East Coast, Central, Mountain, West Coast, Hawaii
Goal: 300 enriched leads per timezone = 1500 total
"""
import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

APOLLO_KEY = os.getenv("APOLLO_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Timezone regions
TIMEZONE_REGIONS = {
    "eastern": [
        "Florida, United States",
        "Georgia, United States",
        "North Carolina, United States",
        "South Carolina, United States",
        "Virginia, United States",
        "New York, United States",
        "Pennsylvania, United States",
        "Ohio, United States",
        "Michigan, United States",
        "New Jersey, United States",
    ],
    "central": [
        "Texas, United States",
        "Illinois, United States",
        "Tennessee, United States",
        "Alabama, United States",
        "Louisiana, United States",
        "Missouri, United States",
        "Wisconsin, United States",
        "Minnesota, United States",
        "Iowa, United States",
        "Kansas, United States",
    ],
    "mountain": [
        "Colorado, United States",
        "Arizona, United States",
        "Utah, United States",
        "New Mexico, United States",
        "Nevada, United States",
        "Idaho, United States",
        "Montana, United States",
        "Wyoming, United States",
    ],
    "pacific": [
        "California, United States",
        "Washington, United States",
        "Oregon, United States",
    ],
    "hawaii": [
        "Hawaii, United States",
    ]
}

NICHES = [
    "HVAC contractors",
    "Roofing companies",
    "Plumbing services",
    "Electrical contractors",
    "General contractors",
    "Landscaping companies",
    "Pool service companies",
    "Pest control services",
]

def apollo_org_search(keywords, location, per_page=100):
    """Search Apollo for companies"""
    if not APOLLO_KEY:
        print("   ⚠️ No Apollo API key!")
        return []
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_companies/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": APOLLO_KEY,
                "q_keywords": keywords,
                "organization_locations": [location],
                "per_page": per_page,
                "organization_num_employees_ranges": ["1,10", "11,50", "51,100", "101,200"]
            },
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get("organizations", [])
        else:
            print(f"   ❌ Apollo error: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Request error: {e}")
    return []

def apollo_enrich_company(company_name):
    """Get decision maker for a company"""
    if not APOLLO_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": APOLLO_KEY,
                "q_organization_name": company_name,
                "person_titles": ["Owner", "CEO", "President", "General Manager", "Operations Manager"],
                "per_page": 1
            },
            timeout=30
        )
        if resp.status_code == 200:
            people = resp.json().get("people", [])
            if people:
                p = people[0]
                return {
                    "decision_maker": p.get("name"),
                    "title": p.get("title"),
                    "enriched_email": p.get("email"),
                    "enriched_phone": p.get("phone_numbers", [{}])[0].get("sanitized_number") if p.get("phone_numbers") else None,
                    "linkedin_url": p.get("linkedin_url")
                }
    except:
        pass
    return None

def main():
    print("="*70)
    print("🔥 MASS PROSPECTOR - 300 LEADS PER TIMEZONE 🔥")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%I:%M %p ET')}")
    print()
    
    stats = {tz: {"prospected": 0, "enriched": 0} for tz in TIMEZONE_REGIONS}
    total_new = 0
    total_enriched = 0
    
    for timezone, regions in TIMEZONE_REGIONS.items():
        print(f"\n{'='*50}")
        print(f"📍 TIMEZONE: {timezone.upper()}")
        print(f"{'='*50}")
        
        tz_count = 0
        tz_enriched = 0
        
        for region in regions:
            if tz_count >= 300:  # Cap per timezone
                break
                
            for niche in NICHES:
                if tz_count >= 300:
                    break
                    
                print(f"\n   🔍 {region} / {niche}...")
                orgs = apollo_org_search(niche, region, per_page=50)
                
                for org in orgs:
                    if tz_count >= 300:
                        break
                        
                    company = org.get("name", "")
                    if not company:
                        continue
                    
                    # Check if exists
                    try:
                        existing = client.table("leads").select("id").eq("company_name", company).execute()
                        if existing.data:
                            continue
                    except:
                        continue
                    
                    # Enrich with decision maker (first 50 per timezone)
                    enrichment = None
                    if tz_enriched < 50:
                        enrichment = apollo_enrich_company(company)
                        if enrichment:
                            tz_enriched += 1
                    
                    # Insert lead
                    lead_data = {
                        "company_name": company,
                        "website": org.get("website_url"),
                        "phone": org.get("phone"),
                        "industry": niche,
                        "city": org.get("city"),
                        "state": org.get("state"),
                        "status": "enriched" if enrichment else "needs_enrichment",
                        "source": f"mass_prospect_{timezone}",
                        "agent_research": json.dumps(enrichment) if enrichment else None
                    }
                    if enrichment and enrichment.get("enriched_email"):
                        lead_data["email"] = enrichment["enriched_email"]
                    
                    try:
                        client.table("leads").insert(lead_data).execute()
                        tz_count += 1
                        total_new += 1
                        if enrichment:
                            total_enriched += 1
                        
                        if tz_count % 25 == 0:
                            print(f"      ✅ {tz_count} leads added for {timezone}")
                    except Exception as e:
                        pass
                
                time.sleep(0.5)  # Rate limit
        
        stats[timezone]["prospected"] = tz_count
        stats[timezone]["enriched"] = tz_enriched
        print(f"\n   📊 {timezone.upper()}: {tz_count} prospected, {tz_enriched} enriched")
    
    print("\n" + "="*70)
    print("🏁 MASS PROSPECTING COMPLETE!")
    print("="*70)
    print(f"\nTIMEZONE BREAKDOWN:")
    for tz, s in stats.items():
        print(f"   {tz.upper()}: {s['prospected']} leads, {s['enriched']} enriched")
    print(f"\n📊 TOTAL NEW LEADS: {total_new}")
    print(f"🔬 TOTAL ENRICHED: {total_enriched}")
    print("="*70)
    
    return stats

if __name__ == "__main__":
    main()
