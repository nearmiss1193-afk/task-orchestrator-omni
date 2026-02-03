import json
import os
from datetime import datetime
from collections import Counter

class EmpireBrain:
    """
    The Self-Learning Core.
    Analyzes outreach logs to optimize future strategy.
    """
    
    def __init__(self, log_file="brain_log.json", config_file="strategy_config.json"):
        self.log_file = log_file
        self.config_file = config_file
        self.default_strategy = {
            "focus_niche": "plumber",
            "email_template_version": "v1_sarah_intro",
            "call_window_start": 8,
            "min_pacing_seconds": 120
        }

    def load_memory(self):
        """Loads past experiences (logs)."""
        if not os.path.exists(self.log_file):
            return []
        
        memories = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    memories.append(json.loads(line))
                except:
                    continue
        return memories

    def reflect_and_optimize(self):
        """Analyzes memory and updates strategy."""
        memories = self.load_memory()
        if not memories:
            print("🧠 [BRAIN] No experiences yet. Stick to default strategy.")
            self._save_strategy(self.default_strategy)
            return self.default_strategy

        print(f"🧠 [BRAIN] Reflecting on {len(memories)} experiences...")
        
        # 1. Analyze Success by Industry
        successes = [m for m in memories if m.get("type") == "outreach_success"]
        industries = []
        for s in successes:
            # Infer industry from company name or metadata if available
            # For now, simple keyword match
            name = s.get("company", "").lower()
            if "plumb" in name: industries.append("plumber")
            elif "cool" in name or "heat" in name or "hvac" in name: industries.append("hvac")
            elif "roof" in name: industries.append("roofer")
            else: industries.append("general")
            
        if industries:
            best_niche = Counter(industries).most_common(1)[0][0]
            print(f"   💡 Insight: '{best_niche}' is converting best.")
        else:
            best_niche = self.default_strategy["focus_niche"]

        # 2. Update Strategy
        new_strategy = self.default_strategy.copy()
        new_strategy["focus_niche"] = best_niche
        # Future: Adjust pacing based on failure rates, etc.

        self._save_strategy(new_strategy)
        self._save_strategy(new_strategy)
        return new_strategy

    def get_asset_map(self, niche):
        """Returns the correct landing page, assets, and branding for a niche."""
        # TODO: Move these URLs to a centralized config or env once deployed
        assets = {
            "plumber": {
                "landing_page": "https://top-local-plumber.vercel.app/",
                "video_link": "https://top-local-plumber.vercel.app/#video",
                "branding": {
                    "sender": "Daniel from Plumber AI",
                    "company": "Plumber Automation Systems",
                    "headline": "Stop losing plumbing jobs to voicemail."
                }
            },
            "hvac": {
                "landing_page": "https://fl-hvac-demo.vercel.app/",
                "video_link": "https://fl-hvac-demo.vercel.app/#video",
                "branding": {
                    "sender": "Daniel from HVAC Flow",
                    "company": "HVAC Growth Engine",
                    "headline": "Capture every AC repair call, 24/7."
                }
            },
            "roofer": {
                "landing_page": "https://best-local-roofer.vercel.app/",
                "video_link": "https://best-local-roofer.vercel.app/#video",
                "branding": {
                    "sender": "Daniel from Roofer Scale",
                    "company": "Roofing AI Partners",
                    "headline": "Book more roof inspections automatically."
                }
            },
            "alf": {
                "landing_page": "https://senior-living-growth.vercel.app/",
                "video_link": "https://senior-living-growth.vercel.app/#video",
                "branding": {
                    "sender": "Daniel from Senior Growth",
                    "company": "ALF Placement AI",
                    "headline": "Fill your beds with qualified families."
                }
            }
        }
        return assets.get(niche, assets["plumber"]) # Fallback to plumber


    def _save_strategy(self, strategy):
        with open(self.config_file, "w") as f:
            json.dump(strategy, f, indent=2)

if __name__ == "__main__":
    brain = EmpireBrain()
    brain.reflect_and_optimize()
