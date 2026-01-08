
"""
ZONAL PROSPECT HUNTER
=====================
Generate prospects by time zone to enable "Follow the Sun" calling.
"""
import os
import json
import requests
import argparse
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GROK_API_KEY = os.getenv('GROK_API_KEY')

ZONES = {
    "midwest": {
        "cities": ["Chicago, IL", "Columbus, OH", "Detroit, MI", "St. Louis, MO", "Minneapolis, MN", "Nashville, TN", "Indianapolis, IN"],
        "prompt_suffix": "Ensure these are in the Midwest (Central Time). CRITICAL: DO NOT include any companies from Texas."
    },
    "west_coast": {
        "cities": ["Los Angeles, CA", "Seattle, WA", "Portland, OR", "Phoenix, AZ", "Las Vegas, NV", "San Diego, CA", "Sacramento, CA"],
        "prompt_suffix": "Ensure these are in the Pacific or Mountain Time zones. CRITICAL: DO NOT include any companies from Texas."
    }
}

def generate_prospects_for_city(city: str, suffix: str, count: int = 5) -> list:
    prompt = f"""Generate {count} realistic HVAC company prospects in {city}.
{suffix}

For each company provide:
- company_name: Realistic local business name
- owner_name: Realistic owner/manager name
- email: firstname@companywebsite.com format
- phone: 10-digit phone starting with area code for {city}
- estimated_revenue: Annual revenue estimate
- employees: Employee count estimate

Return as JSON array."""

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
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                prospects = json.loads(json_match.group())
                for p in prospects:
                    # Clean city/state
                    if ',' in city:
                        p['city'] = city.split(',')[0].strip()
                        p['state'] = city.split(',')[1].strip()
                    else:
                        p['city'] = city
                        p['state'] = ''
                    p['industry'] = "HVAC"
                return prospects
    except Exception as e:
        print(f"[ERROR] {city}: {e}")
    return []

def hunt(zone_name):
    if zone_name not in ZONES:
        print(f"Unknown zone: {zone_name}")
        return

    zone = ZONES[zone_name]
    print(f"🏹 Hunting in {zone_name.upper()}...")
    
    all_prospects = []
    for city in zone['cities']:
        print(f"  Searching {city}...")
        results = generate_prospects_for_city(city, zone['prompt_suffix'])
        all_prospects.extend(results)
        print(f"    Found {len(results)}")
        
    filename = f"prospects_{zone_name}.json"
    with open(filename, "w") as f:
        json.dump(all_prospects, f, indent=2)
    print(f"✅ Saved {len(all_prospects)} leads to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("zone", choices=ZONES.keys())
    args = parser.parse_args()
    hunt(args.zone)
