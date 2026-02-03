import json
import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "niche_config")

class KnowledgeInjector:
    def __init__(self, vertical="hvac"):
        self.vertical = vertical
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self):
        """Loads the specific JSON config for the vertical."""
        path = os.path.join(CONFIG_DIR, f"{self.vertical}.json")
        if not os.path.exists(path):
            print(f"⚠️ Warning: Config for '{self.vertical}' not found at {path}. Defaulting to HVAC Generic.")
            return {}
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
                print(f"📂 Loaded Knowledge Module: {self.vertical.upper()}")
                return data
        except Exception as e:
            print(f"❌ Error loading knowledge: {e}")
            return {}

    def mount_knowledge(self):
        """
        Returns a System Prompt segment with the injected knowledge.
        """
        if not self.knowledge:
            return "<!-- NO VERTICAL KNOWLEDGE MOUNTED -->"

        print(f"💉 Injecting {self.vertical.upper()} Knowledge Base...")
        
        # Format Compliance
        compliance_text = "\n".join([f"- {c}" for c in self.knowledge.get('compliance', [])])
        
        # Format Pricing
        pricing_text = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k,v in self.knowledge.get('pricing', {}).items()])

        prompt_segment = f"""
        --- INDUSTRY KNOWLEDGE BASE ({self.vertical.upper()}) ---
        
        1. WINNING OFFER:
        "{self.knowledge.get('winning_offer', 'N/A')}"

        2. CORE PAIN POINTS:
        {", ".join(self.knowledge.get('pain_points', []))}

        3. LOCAL CODES & REGULATIONS:
        {compliance_text}
        
        4. STANDARD PRICING (ESTIMATES):
        {pricing_text}
        
        5. OBJECTION HANDLERS:
        """
        
        for objection, rebuttal in self.knowledge.get("objections", {}).items():
            prompt_segment += f"- If customer says '{objection}', you say: '{rebuttal}'\n"
            
        print("✅ Knowledge Mounted Successfully.")
        return prompt_segment

if __name__ == "__main__":
    # Test Injection
    print("\n--- TEST: ROOFING ---")
    injector = KnowledgeInjector("roofing")
    print(injector.mount_knowledge())

    print("\n--- TEST: SOLAR ---")
    injector = KnowledgeInjector("solar")
    print(injector.mount_knowledge())
