"""
SCALE PROSPECT HUNTER - 50+ LEADS
=================================
Generate 50+ high-value HVAC prospects across Florida.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')

FLORIDA_CITIES = [
    "Tampa", "Orlando", "Jacksonville", "Miami", "Fort Lauderdale",
    "West Palm Beach", "St. Petersburg", "Clearwater", "Sarasota", "Naples",
    "Fort Myers", "Lakeland", "Gainesville", "Tallahassee", "Pensacola",
    "Daytona Beach", "Melbourne", "Palm Bay", "Ocala", "Deltona",
    "Port St. Lucie", "Cape Coral", "Hollywood", "Pembroke Pines", "Coral Springs"
]

INDUSTRIES = ["HVAC", "Plumbing", "Roofing", "Electrical"]


def generate_prospects_for_city(city: str, industry: str = "HVAC", count: int = 3) -> list:
    """Generate prospects for a city using Grok"""
    
    prompt = f"""Generate {count} realistic {industry} company prospects in {city}, Florida.

For each company provide:
- company_name: Realistic local business name
- owner_name: Realistic owner/manager name
- email: firstname@companywebsite.com format
- phone: 10-digit phone starting with area code for {city} FL
- estimated_revenue: Annual revenue estimate
- employees: Employee count estimate

Return as JSON array. Make names sound authentic for Florida businesses."""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                prospects = json.loads(json_match.group())
                for p in prospects:
                    p['city'] = city
                    p['state'] = 'FL'
                    p['industry'] = industry
                return prospects
    except Exception as e:
        print(f"[ERROR] {city}: {e}")
    
    return []


def generate_50_prospects():
    """Generate 50+ prospects across Florida"""
    
    print(f"{'='*50}")
    print(f"[HUNTER] Generating 50+ prospects - {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    all_prospects = []
    
    # Generate 2-3 per city for top 20 cities
    for city in FLORIDA_CITIES[:20]:
        print(f"[HUNTER] Searching {city}...")
        prospects = generate_prospects_for_city(city, "HVAC", 3)
        all_prospects.extend(prospects)
        print(f"  Found {len(prospects)} prospects")
        
        if len(all_prospects) >= 50:
            break
    
    # Save results
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_prospects": len(all_prospects),
        "prospects": all_prospects
    }
    
    filename = f"campaign_data/prospects_50_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("campaign_data", exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    # Also update campaign_prospects.json
    campaign_format = []
    for p in all_prospects:
        campaign_format.append({
            "name": p.get('owner_name', 'Owner'),
            "email": p.get('email'),
            "company": p.get('company_name'),
            "city": p.get('city'),
            "phone": p.get('phone'),
            "industry": p.get('industry', 'HVAC')
        })
    
    with open("campaign_prospects.json", "w") as f:
        json.dump(campaign_format, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"[HUNTER] COMPLETE!")
    print(f"  Total prospects: {len(all_prospects)}")
    print(f"  Saved to: {filename}")
    print(f"  Updated: campaign_prospects.json")
    print(f"{'='*50}")
    
    return all_prospects


if __name__ == "__main__":
    prospects = generate_50_prospects()
    
    print("\nTop 10 prospects:")
    for p in prospects[:10]:
        print(f"  - {p.get('company_name')} ({p.get('city')}) - {p.get('email')}")
