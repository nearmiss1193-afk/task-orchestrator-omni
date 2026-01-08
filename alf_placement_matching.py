"""
ALF PLACEMENT MATCHING
======================
Advanced scoring algorithm to match families with facilities.
"""
import os
import json
from datetime import datetime
from typing import List, Dict

# Sample facilities database
ALF_DATABASE = [
    {
        "id": "sunrise_tampa",
        "name": "Sunrise Senior Living Tampa",
        "price_min": 4000,
        "price_max": 7000,
        "care_levels": ["independent", "assisted", "memory"],
        "rating": 4.5,
        "beds_available": 8,
        "specialties": ["dementia", "diabetes", "mobility"],
        "amenities": ["pool", "gym", "garden", "chapel"],
        "pet_friendly": True,
        "medicaid_accepted": False,
        "location": {"lat": 27.95, "lng": -82.46}
    },
    {
        "id": "brookdale_tampa",
        "name": "Brookdale Tampa",
        "price_min": 3500,
        "price_max": 6000,
        "care_levels": ["assisted", "memory"],
        "rating": 4.2,
        "beds_available": 12,
        "specialties": ["dementia", "stroke_recovery"],
        "amenities": ["garden", "library", "activities"],
        "pet_friendly": False,
        "medicaid_accepted": True,
        "location": {"lat": 28.02, "lng": -82.52}
    },
    {
        "id": "atria_tampa",
        "name": "Atria Senior Living Tampa",
        "price_min": 4500,
        "price_max": 7500,
        "care_levels": ["independent", "assisted"],
        "rating": 4.6,
        "beds_available": 5,
        "specialties": ["active seniors", "couples"],
        "amenities": ["pool", "gym", "restaurant", "salon", "transportation"],
        "pet_friendly": True,
        "medicaid_accepted": False,
        "location": {"lat": 27.89, "lng": -82.39}
    }
]


def score_facility(facility: dict, requirements: dict) -> dict:
    """Score a facility against family requirements"""
    
    score = 0
    max_score = 100
    breakdown = {}
    
    # Budget fit (30 points)
    budget = requirements.get('budget', 5000)
    if facility['price_min'] <= budget <= facility['price_max']:
        budget_score = 30
    elif budget >= facility['price_min']:
        budget_score = 20  # Can afford minimum
    else:
        budget_score = 0
    score += budget_score
    breakdown['budget_fit'] = budget_score
    
    # Care level match (25 points)
    required_care = requirements.get('care_level', 'assisted')
    if required_care in facility['care_levels']:
        care_score = 25
    else:
        care_score = 0
    score += care_score
    breakdown['care_level'] = care_score
    
    # Rating (15 points)
    min_rating = requirements.get('min_rating', 4.0)
    if facility['rating'] >= min_rating:
        rating_score = 15
    elif facility['rating'] >= min_rating - 0.5:
        rating_score = 10
    else:
        rating_score = 5
    score += rating_score
    breakdown['rating'] = rating_score
    
    # Availability (10 points)
    if facility['beds_available'] > 0:
        avail_score = 10
    else:
        avail_score = 0
    score += avail_score
    breakdown['availability'] = avail_score
    
    # Specialties match (10 points)
    needed_specialties = requirements.get('specialties', [])
    if needed_specialties:
        matches = sum(1 for s in needed_specialties if s in facility['specialties'])
        specialty_score = int((matches / len(needed_specialties)) * 10)
    else:
        specialty_score = 10
    score += specialty_score
    breakdown['specialties'] = specialty_score
    
    # Preferences (10 points)
    pref_score = 0
    if requirements.get('pet_friendly') and facility['pet_friendly']:
        pref_score += 5
    if requirements.get('needs_medicaid') and facility['medicaid_accepted']:
        pref_score += 5
    elif not requirements.get('needs_medicaid'):
        pref_score += 5
    score += pref_score
    breakdown['preferences'] = pref_score
    
    return {
        "facility_id": facility['id'],
        "facility_name": facility['name'],
        "total_score": score,
        "score_percentage": round(score / max_score * 100, 1),
        "breakdown": breakdown,
        "price_range": f"${facility['price_min']}-${facility['price_max']}",
        "beds_available": facility['beds_available']
    }


def find_best_matches(requirements: dict, limit: int = 5) -> List[dict]:
    """Find best matching facilities for given requirements"""
    
    scores = []
    
    for facility in ALF_DATABASE:
        result = score_facility(facility, requirements)
        if result['total_score'] > 0:
            scores.append(result)
    
    # Sort by score
    scores.sort(key=lambda x: x['total_score'], reverse=True)
    
    return scores[:limit]


def generate_match_report(family: dict, requirements: dict) -> str:
    """Generate a match report for a family"""
    
    matches = find_best_matches(requirements)
    
    report = f"""
# ALF Match Report for {family.get('name', 'Family')}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Requirements Summary
- Budget: ${requirements.get('budget', 'Not specified')}/month
- Care Level: {requirements.get('care_level', 'Not specified')}
- Minimum Rating: {requirements.get('min_rating', 4.0)} stars
- Special Needs: {', '.join(requirements.get('specialties', [])) or 'None'}
- Pet Friendly: {'Yes' if requirements.get('pet_friendly') else 'No'}
- Medicaid: {'Required' if requirements.get('needs_medicaid') else 'Not required'}

## Top Matches

"""
    
    for i, match in enumerate(matches, 1):
        report += f"""### {i}. {match['facility_name']}
- **Match Score:** {match['score_percentage']}%
- **Price Range:** {match['price_range']}/month
- **Beds Available:** {match['beds_available']}
- **Score Breakdown:**
"""
        for category, points in match['breakdown'].items():
            report += f"  - {category.replace('_', ' ').title()}: {points} pts\n"
        report += "\n"
    
    report += """
## Next Steps
1. Schedule tours at top matches
2. Prepare questions for each facility
3. Review contracts and pricing details

*Contact Sarah at (863) 213-2505 for tour scheduling*
"""
    
    return report


if __name__ == "__main__":
    test_requirements = {
        "budget": 5500,
        "care_level": "assisted",
        "min_rating": 4.0,
        "specialties": ["dementia"],
        "pet_friendly": True,
        "needs_medicaid": False
    }
    
    test_family = {"name": "Johnson Family"}
    
    matches = find_best_matches(test_requirements)
    print("Top Matches:")
    for m in matches:
        print(f"  {m['facility_name']}: {m['score_percentage']}% match")
    
    report = generate_match_report(test_family, test_requirements)
    print(report)
