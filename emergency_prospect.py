"""
EMERGENCY PROSPECTING LAUNCH
Runs GHL Prospector via browser automation to generate audit reports NOW.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.web.ghl_prospector import GHLProspector
from dotenv import load_dotenv
load_dotenv()

# Target businesses to prospect immediately
TARGETS = [
    ("Johnson's HVAC Repair", "Orlando, FL"),
    ("Pro Plumbing Solutions", "Tampa, FL"),
    ("Elite Roofing Contractors", "Jacksonville, FL"),
    ("Florida Cool Air Services", "Miami, FL"),
    ("Sunshine State Plumbing", "Fort Lauderdale, FL"),
]

def run_emergency_prospecting():
    print("="*60)
    print("🚨 EMERGENCY PROSPECTING LAUNCH")
    print("="*60)
    print(f"   Targets: {len(TARGETS)} businesses")
    print("   Mode: Browser Automation (Playwright)")
    print("="*60)
    
    prospector = GHLProspector(headless=True)  # Run headless for speed
    
    results = []
    for business, location in TARGETS:
        print(f"\n🎯 Processing: {business}")
        try:
            link = prospector.generate_report(business, location)
            if link:
                results.append({
                    "business": business,
                    "location": location,
                    "audit_link": link,
                    "status": "SUCCESS"
                })
                print(f"   ✅ Got link: {link[:50]}...")
            else:
                results.append({
                    "business": business,
                    "location": location,
                    "audit_link": None,
                    "status": "FAILED"
                })
                print(f"   ❌ No link generated")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "business": business,
                "location": location,
                "audit_link": None,
                "status": f"ERROR: {e}"
            })
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    success = len([r for r in results if r["status"] == "SUCCESS"])
    print(f"   Success: {success}/{len(results)}")
    
    for r in results:
        status_icon = "✅" if r["status"] == "SUCCESS" else "❌"
        print(f"   {status_icon} {r['business']}: {r['status']}")
    
    return results

if __name__ == "__main__":
    run_emergency_prospecting()
