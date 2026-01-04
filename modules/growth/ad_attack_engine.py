import os
import random
import sys
import json
from datetime import datetime

# Allow import from sibling module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from media.video_prompter import VideoPrompter
from communication.sovereign_dispatch import dispatcher

# --- SIMULATED SCRAPED DATA (PREDATOR 1-STAR FEED) ---
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
    }
]

class AdAttackEngine:
    def __init__(self):
        print("⚔️ Initializing Ad Attack Engine (Predator V35.0 - Sovereign Edition)...")
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
        from qa.link_validator import validate_link
        target_url = "https://empire-sovereign-cloud.vercel.app"
        
        if not validate_link(target_url):
            print("❌ ABORTING: Landing Page is DOWN. Cannot run ads.")
            # Notify User via Sovereign Dispatch
            dispatcher.send_email("nearmiss1193@gmail.com", "🚨 URGENT: Landing Page Down", "Ad Attack aborted because site is unreachable.")
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
        for attempt in range(3):
            try:
                return self.prompter.generate_prompt(concept, vibe="cinematic_commercial")
            except Exception as e:
                print(f"   ⚠️ Model Overload (Attempt {attempt+1}/3): {e}. Retrying...")
                import time; time.sleep(2)
        return "Visual Prompt Unavailable (System Overload)"

    def save_and_notify(self, ads):
        """Saves report locally AND triggers Sovereign Dispatch notification."""
        filename = "campaign_results_v1.md"
        report_content = f"# ⚔️ AD ATTACK REPORT ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        html_body = "<h2>⚔️ Ad Attack Campaign Generated</h2><ul>"
        
        try:
            # 1. Save Local Markdown
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_content)
                for i, ad in enumerate(ads):
                    block = f"## Ad #{i+1}: {ad['target_pain']}\n**Hook:** {ad['headline']}\n**Visual:** `{ad['video_prompt']}`\n---\n"
                    f.write(block)
                    
                    # Add to email HTML
                    html_body += f"<li><strong>{ad['target_pain']}</strong>: {ad['headline']}</li>"
            
            print(f"✅ Campaign Report saved to: {filename}")
            
            # 2. Sovereign Dispatch (Email + SMS)
            html_body += f"</ul><p><strong>Full report saved to:</strong> {filename}</p>"
            
            print("   📨 Dispatching Alerts via Sovereign Network...")
            dispatcher.send_email(
                to_email="nearmiss1193@gmail.com", 
                subject=f"⚔️ Campaign Ready: {len(ads)} Ads Generated", 
                html_body=html_body
            )
            
            dispatcher.send_sms(
                to_phone="+13529368152",
                body=f"⚔️ Ad Attack Complete. {len(ads)} ads generated for verification. Check inbox."
            )
            
        except Exception as e:
            print(f"❌ Failed to save/notify: {e}")

if __name__ == "__main__":
    engine = AdAttackEngine()
    ads = engine.scan_and_attack("Lazy HVAC Boys LLC")
    if ads:
        engine.save_and_notify(ads)
