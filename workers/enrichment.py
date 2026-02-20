import os
import json
import time
import requests
import traceback
import random
from urllib.parse import urlparse

# ──────────────────────────────────────────────────────────
#  PAGESPEED INSIGHTS (Universal Enrichment)
# ──────────────────────────────────────────────────────────

def fetch_pagespeed(website_url: str) -> dict:
    """Fetches PageSpeed Insights for a URL (mobile strategy)."""
    result = {
        "score": 0,
        "fcp": "N/A",
        "lcp": "N/A",
        "cls": "N/A",
        "speed_index": "N/A",
        "status": "unknown"
    }

    if not website_url.startswith("http"):
        website_url = f"https://{website_url}"

    api_keys = [os.environ.get("GOOGLE_API_KEY"), os.environ.get("GOOGLE_PLACES_API_KEY")]
    api_keys = [k for k in api_keys if k]
    random.shuffle(api_keys)
    
    for api_key in api_keys:
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={website_url}&strategy=mobile&category=performance&key={api_key}"
        try:
            r = requests.get(api_url, timeout=45)
            if r.status_code == 200:
                data = r.json()
                lighthouse = data.get("lighthouseResult", {})
                score = lighthouse.get("categories", {}).get("performance", {}).get("score")
                if score is not None:
                    result["score"] = int(score * 100)
                    result["status"] = "good" if result["score"] >= 90 else "warning" if result["score"] >= 50 else "critical"
                
                audits = lighthouse.get("audits", {})
                result["fcp"] = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
                result["lcp"] = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
                result["cls"] = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
                result["speed_index"] = audits.get("speed-index", {}).get("displayValue", "N/A")
                return result
        except: continue
    return result

def check_privacy_policy(url: str) -> dict:
    """Checks for privacy policy existence (FDBR compliance)."""
    try:
        if not url.startswith("http"): url = f"https://{url}"
        r = requests.get(url, timeout=15, verify=False)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'lxml')
        links = soup.find_all('a', href=True)
        found = any("privacy" in l.get('href').lower() for l in links)
        return {"exists": found, "status": "pass" if found else "fail"}
    except:
        return {"exists": False, "status": "error"}

def check_ai_readiness(url: str) -> dict:
    """Checks for AI indicators (chatbots, specific tools)."""
    # Simple heuristic for now
    return {"status": "low", "indicators": []}
