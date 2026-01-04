import os
import random
import sys

# Allow import from sibling module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from media.video_prompter import VideoPrompter

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
        self.prompter = VideoPrompter()
        self.grievance_map = {
            "Tardiness": {
                "hook": "I saw your 1-star review about 'late techs'. Fix it today?",
                "angle": "Our AI Dispatcher texts customers instantly when techs are late, saving the relationship.",
                "visual_concept": "Split screen: Frazzled human dispatcher vs Calm AI Dashboard managing routes"
            },
            "Hidden Fees": {
                "hook": "Are price complaints hurting your Google Rating?",
                "angle": "Our 'Transparent Quote' bot sends approved PDF estimates before the truck rolls.",
                "visual_concept": "Close up of a 5-Star Review that says 'Honest pricing!'"
            },
            "Ghosting": {
                "hook": "How many leads did you miss after 5pm yesterday?",
                "angle": "Our AI Voice Agent answers 24/7. Never miss a $10k install again.",
                "visual_concept": "Office lights turning off at 5pm, but the phone keeps ringing and AI answers it"
            }
        }

    def scan_and_attack(self, competitor_name="Generic Inc"):
        print(f"   Searching 1-Star Reviews for: {competitor_name}...")
        # Mocking the scrape results
        found_grievances = ["Tardiness", "Hidden Fees"]
        
        attack_ads = []
        for g in found_grievances:
            data = self.grievance_map.get(g)
            if data:
                # Generate Cinematic Visual
                video_prompt = self.prompter.generate_prompt(
                    data['visual_concept'], 
                    vibe="cinematic_commercial"
                )
                
                ad = {
                    "target_pain": g,
                    "headline": data['hook'],
                    "body": data['angle'],
                    "video_prompt": video_prompt
                }
                attack_ads.append(ad)
        
        return attack_ads

if __name__ == "__main__":
    engine = AdAttackEngine()
    ads = engine.scan_and_attack("Lazy HVAC Boys LLC")
    
    print("\n--- ATTACK CAMPAIGN GENERATED ---\n")
    for i, ad in enumerate(ads):
        print(f"AD #{i+1} (Targeting: {ad['target_pain']})")
        print(f"HEADLINE: {ad['headline']}")
        print(f"COPY:     {ad['body']}")
        print(f"🎥 SCENE:  {ad['video_prompt']}")
        print("---------------------------------")
