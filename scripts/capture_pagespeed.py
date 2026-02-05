#!/usr/bin/env python3
"""
Capture PageSpeed screenshots for email outreach.
Uses Google PageSpeed Insights API to get performance data.
"""
import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# Prospects to test
PROSPECTS = [
    {"company": "Vanguard Plumbing & Air", "website": "vanguardplumbingair.com"},
    {"company": "Five Points Roofing", "website": "fivepointsroofingfl.com"},
    {"company": "Original Pro Plumbing", "website": "originalplumber.com"},
    {"company": "Hunter Plumbing Inc", "website": "hunterplumbinginc.com"},
    {"company": "Andress Electric", "website": "andresselectric.com"},
    {"company": "Leaf Electric", "website": "leafelectricfl.com"},
    {"company": "Curry Plumbing", "website": "curryplumbing.com"},
    {"company": "B&W Plumbing LLC", "website": "bandwplumbing.com"},
    {"company": "Trimm Roofing", "website": "trimmroofing.com"},
    {"company": "Lakeland AC", "website": "thelakelandac.com"},
]

# Output directory
OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\pagespeed_results"

def run_pagespeed_test(website, strategy="mobile", api_key=None):
    """
    Run PageSpeed Insights test and get results.
    Returns performance score and key metrics.
    Falls back to alternate API key if primary fails.
    """
    # Try primary key first, then fallback
    api_keys = [
        api_key,
        "AIzaSyCtDhszpASBGBrW7A7tuX3N8txDflx_i4o",  # Empire-Email-Integration (WORKS)
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GOOGLE_API_KEY_ALT"),
        "AIzaSyALaxJstr7hiyyC52zTZOd2ymow5v1-PKY",
        "AIzaSyB_WzpN1ASQssu_9ccfweWFPfoRknVUlHU"
    ]
    api_keys = [k for k in api_keys if k]  # Remove None values
    
    url = f"https://{website}"
    encoded_url = quote(url, safe='')
    
    last_error = None
    for key in api_keys:
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&strategy={strategy}&key={key}"
        
        try:
            response = requests.get(api_url, timeout=120)
            data = response.json()
            
            if "error" in data:
                last_error = data["error"]["message"]
                continue  # Try next key
            
            # Extract key metrics
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})
            
            performance_score = categories.get("performance", {}).get("score", 0)
            if performance_score:
                performance_score = int(performance_score * 100)
            
            # Get timing metrics
            fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
            lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
            cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
            speed_index = audits.get("speed-index", {}).get("displayValue", "N/A")
            
            # Get screenshot
            screenshot = audits.get("final-screenshot", {}).get("details", {}).get("data", "")
            
            return {
                "website": website,
                "strategy": strategy,
                "score": performance_score,
                "fcp": fcp,
                "lcp": lcp,
                "cls": cls,
                "speed_index": speed_index,
                "screenshot": screenshot,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            last_error = str(e)
            continue
    
    return {"error": last_error or "All API keys failed"}

def save_results(prospect, results):
    """Save PageSpeed results to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filename = prospect["company"].replace(" ", "_").replace("&", "and")
    filepath = os.path.join(OUTPUT_DIR, f"{filename}_pagespeed.json")
    
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    
    return filepath

def main():
    print("=" * 70)
    print("PAGESPEED INSIGHTS TESTING")
    print("Testing 10 prospects for email outreach")
    print("=" * 70)
    
    all_results = []
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/10] Testing: {prospect['company']}")
        print(f"        Website: {prospect['website']}")
        
        # Test mobile
        print(f"        Running mobile test...")
        mobile_result = run_pagespeed_test(prospect['website'], 'mobile')
        
        if "error" in mobile_result:
            print(f"        ❌ Error: {mobile_result['error'][:50]}...")
        else:
            print(f"        📱 Mobile Score: {mobile_result['score']}/100")
            print(f"        ⏱️ LCP: {mobile_result['lcp']}")
        
        # Test desktop
        print(f"        Running desktop test...")
        desktop_result = run_pagespeed_test(prospect['website'], 'desktop')
        
        if "error" in desktop_result:
            print(f"        ❌ Error: {desktop_result['error'][:50]}...")
        else:
            print(f"        🖥️ Desktop Score: {desktop_result['score']}/100")
        
        # Save results
        results = {
            "company": prospect["company"],
            "website": prospect["website"],
            "mobile": mobile_result,
            "desktop": desktop_result
        }
        
        filepath = save_results(prospect, results)
        print(f"        💾 Saved: {os.path.basename(filepath)}")
        
        all_results.append(results)
        
        # Rate limiting
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for r in all_results:
        m_score = r['mobile'].get('score', 'ERR') if 'error' not in r['mobile'] else 'ERR'
        d_score = r['desktop'].get('score', 'ERR') if 'error' not in r['desktop'] else 'ERR'
        
        status = "🔴" if isinstance(m_score, int) and m_score < 50 else "🟡" if isinstance(m_score, int) and m_score < 80 else "🟢"
        
        print(f"{status} {r['company']}: Mobile={m_score}, Desktop={d_score}")
    
    print("\n" + "=" * 70)
    print(f"Results saved to: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
