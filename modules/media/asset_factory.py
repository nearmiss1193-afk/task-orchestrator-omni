
import json
import os
import random

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "asset_manifest.json")

class VisualFactory:
    def __init__(self):
        self.assets = self._load_manifest()

    def _load_manifest(self):
        if not os.path.exists(MANIFEST_PATH):
            print(f"⚠️ Manifest not found at {MANIFEST_PATH}")
            return []
        try:
            with open(MANIFEST_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading manifest: {e}")
            return []

    def get_asset(self, category=None, tone=None, tags=None):
        """
        Selects the best asset based on filters.
        """
        candidates = self.assets

        if category:
            candidates = [a for a in candidates if a.get("category") == category]
        
        if tone:
            candidates = [a for a in candidates if a.get("tone") == tone]
            
        if tags:
            # Simple interaction check: if any tag matches
            candidates = [a for a in candidates if any(t in a.get("tags", []) for t in tags)]

        if not candidates:
            print("⚠️ No exact match found. Returning random asset from library.")
            return random.choice(self.assets) if self.assets else None
            
        selected = random.choice(candidates)
        print(f"✅ Asset Selected: {selected['id']} ({selected['description']})")
        return selected

if __name__ == "__main__":
    print("🏭 Visual Asset Factory Initialized...")
    factory = VisualFactory()
    
    print("\n--- Request 1: Urgent Pain Point ---")
    asset1 = factory.get_asset(category="pain_point", tone="Urgent")
    
    print("\n--- Request 2: Community Branding ---")
    asset2 = factory.get_asset(category="community")
    
    print("\n--- Request 3: Specific Tag 'family' ---")
    asset3 = factory.get_asset(tags=["family"])
