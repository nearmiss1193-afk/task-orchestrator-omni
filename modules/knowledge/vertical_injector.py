
import json
import os

# --- KNOWLEDGE BASE REGISTRY ---
# In a real system, these would be separate JSON files or Vector DB entries.
VERTICAL_KNOWLEDGE = {
    "hvac": {
        "codes": "Florida Mechanical Code 2024: Requires SEER2 rating for new installs.",
        "pricing": "Tune-up: $59. Freon Fill: $89/lb. New Unit: Start at $4,500.",
        "objections": {"too_expensive": "We offer 0% financing for 18 months."}
    },
    "roofing": {
        "codes": "Miami-Dade Hurricane Protocol: Shingles must be rated for 130mph winds.",
        "pricing": "Shingle: $4/sqft. Metal: $9/sqft. Tile: $12/sqft.",
        "objections": {"insurance_wont_pay": "We have a public adjuster on staff to handle the claim."}
    },
    "solar": {
        "codes": "Federal ITC 2026: 30% Tax Credit applies to battery storage.",
        "pricing": "$2.80/watt installed. TECO Net Metering is 1:1.",
        "objections": {"moving_soon": "Solar increases home value by 4.1% on average."}
    }
}

class KnowledgeInjector:
    def __init__(self, vertical="hvac"):
        self.vertical = vertical
        self.knowledge = VERTICAL_KNOWLEDGE.get(vertical, {})
        if not self.knowledge:
            print(f"⚠️ Warning: Vertical '{vertical}' not found. Defaulting to Empty.")

    def mount_knowledge(self):
        """
        Returns a System Prompt segment with the injected knowledge.
        """
        print(f"💉 Injecting {self.vertical.upper()} Knowledge Base...")
        
        prompt_segment = f"""
        --- INDUSTRY KNOWLEDGE BASE ({self.vertical.upper()}) ---
        
        1. LOCAL CODES & REGULATIONS:
        {self.knowledge.get('codes', 'N/A')}
        
        2. PRICING & ESTIMATES:
        {self.knowledge.get('pricing', 'N/A')}
        
        3. OBJECTION HANDLERS:
        """
        
        for objection, rebuttal in self.knowledge.get("objections", {}).items():
            prompt_segment += f"- If customer says '{objection}', you say: '{rebuttal}'\n"
            
        print("✅ Knowledge Mounted Successfully.")
        return prompt_segment

if __name__ == "__main__":
    # Test Injection
    injector = KnowledgeInjector("solar")
    print(injector.mount_knowledge())
