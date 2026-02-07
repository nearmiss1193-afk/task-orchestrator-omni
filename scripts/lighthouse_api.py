
import os
import requests
import json
from dotenv import load_dotenv

# Load secrets
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def get_pagespeed_data(url, strategy="mobile"):
    """
    Fetches PageSpeed Insight data for a given URL.
    Returns a dict with key metrics.
    """
    if not API_KEY:
        return {"error": "Missing GOOGLE_API_KEY"}

    params = {
        "url": url,
        "key": API_KEY,
        "strategy": strategy,
        "category": ["performance", "best-practices", "accessibility"]
    }

    print(f"   ⚡ Lighthouse API: Analyzing {url} ({strategy})...")
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        # Scores (0-1 -> 0-100)
        perf_score = int(categories.get("performance", {}).get("score", 0) * 100)
        bp_score = int(categories.get("best-practices", {}).get("score", 0) * 100)
        access_score = int(categories.get("accessibility", {}).get("score", 0) * 100)

        # Metrics
        si = audits.get("speed-index", {}).get("displayValue", "N/A")
        fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
        
        return {
            "performance": perf_score,
            "best_practices": bp_score,
            "accessibility": access_score,
            "speed_index": si,
            "fcp": fcp,
            "raw_json_path": None # To be filled if saved
        }

    except Exception as e:
        print(f"   ❌ Lighthouse Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Test
    res = get_pagespeed_data("https://yourlakelanddentist.com")
    print(json.dumps(res, indent=2))
