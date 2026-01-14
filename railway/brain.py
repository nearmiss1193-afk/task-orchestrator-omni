import os
import requests
import json
from datetime import datetime
from collections import Counter

class EmpireBrain:
    """
    Cloud-Native Brain.
    Uses Supabase for memory and strategy persistence.
    """
    def __init__(self):
        # Support both naming conventions
        self.supabase_url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.default_niche = "hvac" # Default to HVAC as requested

    def _sb_request(self, method, endpoint, data=None):
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        try:
            if method == "GET":
                r = requests.get(f"{self.supabase_url}/rest/v1/{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                r = requests.post(f"{self.supabase_url}/rest/v1/{endpoint}", headers=headers, json=data, timeout=10)
            return r.json() if r.ok else None
        except:
            return None

    def get_strategy(self):
        """Analyze past performance to pick best niche."""
        # 1. Fetch recent learnings
        learnings = self._sb_request("GET", "agent_learnings?select=*&limit=100&order=created_at.desc")
        
        if not learnings:
            print("[BRAIN] No data, defaulting to HVAC")
            return self.default_niche
            
        # 2. Analyze
        # Simple logic: Count most frequent positive outcomes
        successes = [l.get("metadata", {}).get("niche", "hvac") for l in learnings 
                     if l.get("insight_type") in ["email_reply", "call_connected"]]
        
        if successes:
            best_niche = Counter(successes).most_common(1)[0][0]
            print(f"[BRAIN] Optimized Strategy: Focus on {best_niche}")
            return best_niche
        
        return self.default_niche

    def record_outcome(self, outcome_type, niche, details):
        """Save a learning event."""
        payload = {
            "insight_type": outcome_type,
            "description": f"Outcome: {outcome_type} in {niche}",
            "metadata": {"niche": niche, "details": details},
            "created_at": datetime.utcnow().isoformat()
        }
        self._sb_request("POST", "agent_learnings", payload)

    def get_assets(self, niche):
        """Return branding/assets for the niche."""
        # Default map
        assets = {
            "hvac": {
                "keywords": "HVAC contractor", 
                "location": "Florida",
                "brand": "HVAC Flow",
                "landing": "https://fl-hvac-demo.vercel.app/"
            },
            "plumber": {
                "keywords": "Plumbing services", 
                "location": "Texas",
                "brand": "Plumber AI",
                "landing": "https://top-local-plumber.vercel.app/"
            },
            "roofer": {
                "keywords": "Roofing company", 
                "location": "Georgia",
                "brand": "Roofer Scale",
                "landing": "https://best-local-roofer.vercel.app/"
            }
        }
        # Fuzzy match to handle "HVAC contractor" vs "hvac"
        niche_key = "hvac"
        if "plumb" in niche.lower(): niche_key = "plumber"
        if "roof" in niche.lower(): niche_key = "roofer"
        
        return assets.get(niche_key, assets["hvac"])
