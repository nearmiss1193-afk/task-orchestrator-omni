
import os
import random

# --- SIMULATED SCRAPED DATA (PREDATOR 1-STAR FEED) ---
# In production, this comes from an Apify Google Maps Scraper JSON output.
COMPETITOR_REVIEWS = [
    {
        "competitor": "Iceberg HVAC Services",
        "review": "Technician showed up 2 hours late and smelled like smoke. Then charged me $90 just to say I needed a new unit.",
        "stars": 1,
        "date": "2026-01-02"
    },
    {
        "competitor": "Egbert's Cooling",
        "review": "Quoted me $4500 on the phone, but the final bill was $6200. Claimed 'copper prices went up'. Liars.",
        "stars": 1,
        "date": "2026-01-01"
    },
    {
        "competitor": "Global HVAC",
        "review": "My AC is still broken after 3 visits. They just keep refilling the freon and leaving.",
        "stars": 1,
        "date": "2025-12-29"
    }
]

class AdAttackEngine:
    def __init__(self):
        print("⚔️ Initializing Ad Attack Engine (Predator V34.0)...")

    def identify_grievance(self, review_text):
        """
        Extracts the 'Primary Grievance' using simple keyword heuristics (or LLM in V50.0).
        """
        review_lower = review_text.lower()
        if "late" in review_lower or "show up" in review_lower:
            return "Tardiness"
        elif "price" in review_lower or "bill" in review_lower or "cost" in review_lower or "charged" in review_lower:
            return "Hidden Fees"
        elif "broken" in review_lower or "visit" in review_lower or "fix" in review_lower:
            return "Incompetence"
        else:
            return "Poor Service"

    def generate_attack_ad(self, review):
        grievance = self.identify_grievance(review['review'])
        competitor = review['competitor']
        
        print(f"\n🎯 Target: {competitor} | Weakness: {grievance}")
        print(f"   Context: \"{review['review'][:60]}...\"")
        
        # Attack Templates
        if grievance == "Tardiness":
            headline = f"Still Waiting for {competitor}?"
            body = "Our technicians arrive on time, or the service call is FREE. Don't waste your day waiting for the 'maybe' guys."
        elif grievance == "Hidden Fees":
            headline = f"Did {competitor} Change the Price?"
            body = "We guarantee our quote. No 'Copper Surcharges', no 'Fuel Fees', no surprises. The price we say is the price you pay."
        elif grievance == "Incompetence":
            headline = f"{competitor} Can't Fix It?"
            body = "Tired of paying for 'visits' instead of repairs? Our senior techs fix it right the first time, guaranteed."
        else:
            headline = f"Deserve Better Than {competitor}?"
            body = "Experience the V50.0 difference. Instant booking, honest pricing, and local technicians who actually care."
            
        return {
            "headline": headline,
            "primary_text": body,
            "call_to_action": "Book Instantly (We Answer in 2 Seconds)"
        }

if __name__ == "__main__":
    engine = AdAttackEngine()
    
    print("\n--- GENERATING ATTACK CAMPAIGN ---\n")
    for rev in COMPETITOR_REVIEWS:
        ad = engine.generate_attack_ad(rev)
        print(f"📢 HEADLINE: {ad['headline']}")
        print(f"📝 BODY: {ad['primary_text']}")
        print(f"👉 CTA: {ad['call_to_action']}")
