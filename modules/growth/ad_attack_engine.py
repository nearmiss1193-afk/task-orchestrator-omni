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
        print("⚔️ Initializing Ad Attack Engine (Predator V34.1 - Sovereign Optimized)...")
        self.prompter = VideoPrompter()
        self.grievance_map = self._load_grievances()

    def _load_grievances(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "grievance_db.json")
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load Grievance DB: {e}. Using fallback.")
            return {}


    def scan_and_attack(self, competitor_name="Generic Inc"):
        print(f"   Searching 1-Star Reviews for: {competitor_name}...")
        
        # 0. Integrated Verification (The Shopper)
        # Ensure our Landing Page is actually live before generating ads
        from qa.link_validator import validate_link
        target_url = "https://empire-sovereign-cloud.vercel.app"
        if not validate_link(target_url):
            print("❌ ABORTING: Landing Page is DOWN. Cannot run ads.")
            return []

        # Mocking the scrape results
        found_grievances = ["Tardiness", "Hidden Fees"]
        
        attack_ads = []
        for g in found_grievances:
            data = self.grievance_map.get(g)
            if data:
                # Generate Cinematic Visual with SMART RETRY
                video_prompt = self._safe_generate_prompt(data['visual_concept'])
                
                ad = {
                    "target_pain": g,
                    "headline": data['hook'],
                    "body": f"{data['angle']} [Link: {target_url}]",
                    "video_prompt": video_prompt
                }
                attack_ads.append(ad)
        
        return attack_ads

    def _safe_generate_prompt(self, concept):
        # Resilience Logic: 3 Retries
        for attempt in range(3):
            try:
                return self.prompter.generate_prompt(concept, vibe="cinematic_commercial")
            except Exception as e:
                print(f"   ⚠️ Model Overload (Attempt {attempt+1}/3): {e}. Retrying...")
                import time; time.sleep(2 * (attempt + 1)) # Backoff
        
        return "Visual Prompt Unavailable (System Overload)"

    def save_campaign_report(self, ads, filename="campaign_results_v1.md"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# ⚔️ AD ATTACK CAMPAIGN REPORT\n")
                f.write(f"**Date:** {os.environ.get('DATE', 'Today')}\n\n")
                
                for i, ad in enumerate(ads):
                    f.write(f"## Ad #{i+1} (Target: {ad['target_pain']})\n")
                    f.write(f"**Headline:** {ad['headline']}\n")
                    f.write(f"**Copy:** {ad['body']}\n")
                    f.write(f"**🎥 Visual Prompt:** `{ad['video_prompt']}`\n")
                    f.write(f"---\n")
            print(f"✅ Campaign Report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

if __name__ == "__main__":
    engine = AdAttackEngine()
    ads = engine.scan_and_attack("Lazy HVAC Boys LLC")
    engine.save_campaign_report(ads)
