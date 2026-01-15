"""
SEACOAST ALF - SENIOR PLACEMENT AGENT
======================================
AI-powered Assisted Living Facility referral system.
Researches ALFs, matches families, earns placement commissions.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Florida ALF database (sample - would be scraped in production)
FLORIDA_ALFS = {
    "Tampa": [
        {"name": "Sunrise Senior Living Tampa", "beds": 120, "price_range": "$4000-$7000", "rating": 4.5},
        {"name": "Brookdale Tampa", "beds": 85, "price_range": "$3500-$6000", "rating": 4.2},
        {"name": "Atria Senior Living", "beds": 95, "price_range": "$4500-$7500", "rating": 4.6},
    ],
    "Orlando": [
        {"name": "Legacy Pointe Orlando", "beds": 100, "price_range": "$3800-$6500", "rating": 4.3},
        {"name": "Brookdale Dr. Phillips", "beds": 75, "price_range": "$4000-$6800", "rating": 4.4},
    ],
    "Jacksonville": [
        {"name": "Arbor Terrace Ortega", "beds": 80, "price_range": "$3500-$5500", "rating": 4.1},
    ]
}

# Commission structure (typical 100% of first month rent)
COMMISSION_RATES = {
    "assisted_living": 1.0,  # 100% first month
    "memory_care": 1.0,      # 100% first month  
    "independent_living": 0.5  # 50% first month
}


def analyze_family_needs(family_info: dict) -> dict:
    """Use Grok to analyze family needs and match to ALF criteria"""
    
    prompt = f"""Analyze this family's senior care needs and recommend ALF criteria:

Family Info:
- Senior's Age: {family_info.get('senior_age', 'Unknown')}
- Care Level Needed: {family_info.get('care_level', 'Unknown')}
- Budget: {family_info.get('budget', 'Unknown')}
- Location Preference: {family_info.get('location', 'Florida')}
- Special Needs: {family_info.get('special_needs', 'None specified')}

Return JSON with:
- recommended_care_type: (assisted_living, memory_care, or independent_living)
- min_rating: minimum acceptable rating (1-5)
- budget_range: [min, max] monthly
- key_features: list of 3-5 must-have features
- urgency: (immediate, 1-3 months, planning ahead)
"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"[ERROR] Grok analysis failed: {e}")
    
    return {"recommended_care_type": "assisted_living", "min_rating": 4.0}


def find_matching_alfs(criteria: dict, city: str = "Tampa") -> list:
    """Find ALFs matching the criteria"""
    
    alfs = FLORIDA_ALFS.get(city, [])
    matches = []
    
    min_rating = criteria.get('min_rating', 4.0)
    
    for alf in alfs:
        if alf['rating'] >= min_rating:
            matches.append({
                **alf,
                "match_score": alf['rating'] / 5 * 100,
                "estimated_commission": calculate_commission(alf['price_range'])
            })
    
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)


def calculate_commission(price_range: str) -> float:
    """Calculate expected commission from price range"""
    try:
        # Parse "$4000-$7000" format
        parts = price_range.replace("$", "").replace(",", "").split("-")
        avg_price = (int(parts[0]) + int(parts[1])) / 2
        return avg_price * COMMISSION_RATES['assisted_living']
    except:
        return 5000  # Default estimate


def generate_family_report(family_info: dict, matches: list) -> str:
    """Generate a personalized report for the family"""
    
    report = f"""
# Senior Living Options for {family_info.get('family_name', 'Your Family')}

## Recommended Facilities

"""
    for i, alf in enumerate(matches[:5], 1):
        report += f"""
### {i}. {alf['name']}
- **Rating:** {alf['rating']}/5 ⭐
- **Price Range:** {alf['price_range']}/month
- **Available Beds:** {alf['beds']}
- **Match Score:** {alf['match_score']:.0f}%

"""
    
    report += """
## Next Steps
1. Schedule tours at your top 2-3 choices
2. Ask about current availability and waitlist
3. Request a detailed pricing breakdown
4. We'll be with you every step of the way!

*Questions? Call Sarah at +1 (352) 758-5336*
"""
    
    return report


def process_lead(lead: dict) -> dict:
    """Full lead processing pipeline"""
    
    print(f"[ALF] Processing lead: {lead.get('family_name')}")
    
    # 1. Analyze needs via Grok
    criteria = analyze_family_needs(lead)
    print(f"[ALF] Criteria: {criteria}")
    
    # 2. Find matches
    city = lead.get('location', 'Tampa')
    matches = find_matching_alfs(criteria, city)
    print(f"[ALF] Found {len(matches)} matches")
    
    # 3. Generate report
    report = generate_family_report(lead, matches)
    
    # 4. Calculate potential commission
    total_commission = sum(m['estimated_commission'] for m in matches[:3]) / 3
    
    # 5. Send SMS notification
    if lead.get('phone'):
        send_lead_notification(lead, len(matches), total_commission)
    
    return {
        "lead": lead,
        "criteria": criteria,
        "matches": matches,
        "report": report,
        "potential_commission": total_commission
    }


def send_lead_notification(lead: dict, match_count: int, commission: float):
    """Notify about new ALF lead"""
    message = f"🏠 ALF Lead: {lead.get('family_name')} in {lead.get('location', 'FL')} - {match_count} matches, ~${commission:.0f} potential"
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": os.getenv('TEST_PHONE', '+13529368152'),
            "message": message
        })
        print(f"[SMS] Lead notification sent")
    except Exception as e:
        print(f"[ERROR] SMS failed: {e}")


if __name__ == "__main__":
    # Test with sample lead
    test_lead = {
        "family_name": "Johnson Family",
        "senior_age": 78,
        "care_level": "assisted living",
        "budget": "$4000-$6000/month",
        "location": "Tampa",
        "special_needs": "Diabetes management, wheelchair accessible",
        "phone": "+13529368152"
    }
    
    result = process_lead(test_lead)
    print(f"\n{result['report']}")
    print(f"\nPotential Commission: ${result['potential_commission']:.2f}")
