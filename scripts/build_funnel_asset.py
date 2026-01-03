
import os
import sys

# Ensure proper path
sys.path.insert(0, os.getcwd())

from modules.constructor.wiring import WiringTech
from modules.constructor.funnel_forge import FunnelForge

def run():
    print("--- EMPIRE BUILDER INITIATED ---")
    
    niches = ["Plumbers", "Lawyers", "Med Spas"]
    forge = FunnelForge()
    
    if not os.path.exists("output"):
        os.makedirs("output")

    for niche in niches:
        print(f"Building Assets for: {niche}")
        
        # 1. Page
        html = forge.generate_landing_page(niche, "Free Audit", "https://calendly.com/audit")
        
        # 2. Save
        fname = f"output/{niche}_lander.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f" -> Saved {fname}")

    print("--- BUILD COMPLETE ---")

if __name__ == "__main__":
    run()
