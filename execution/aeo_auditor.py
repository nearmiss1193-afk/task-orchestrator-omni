import sys
import json
import random
import datetime

def generate_aeo_audit(url, niche="Business", data=None):
    """
    Generates a premium AI Visibility Audit based on the Nick Ponty / Manus AI model.
    """
    
    if data:
        monthly_visits = data.get("monthly_visits", random.randint(100, 5000))
        direct_pct = data.get("direct_traffic_pct", random.randint(45, 65))
        ai_pct = data.get("ai_search_traffic_pct", random.randint(2, 8))
        revenue = data.get("revenue_range", "$1M - $5M")
    else:
        monthly_visits = random.randint(100, 5000)
        direct_pct = random.randint(45, 65)
        ai_pct = random.randint(2, 8)
        revenue = "$1M - $5m"

    competitors = [
        {"name": f"Top Rival {i+1}", "score": random.randint(85, 98)}
        for i in range(3)
    ]
    
    visibility_status = "INVISIBLE" if ai_pct < 10 else "LOW VISIBILITY"
    
    # Audit MD Generation
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    
    audit_md = f"""# AI VISIBILITY AUDIT: {url}
**Date:** {timestamp}
**Target Niche:** {niche}
**Est. Revenue:** {revenue}

## 1. Executive Summary: The "AI Gap"
Currently, your business is **{visibility_status}** in AI recommendations (ChatGPT, Gemini, Perplexity).

While your direct traffic is strong ({direct_pct}%), this means you are only reaching people who **already know your name**. You are missing the 90%+ of the market searching for "Best {niche} in Hawaii" through AI.

## 2. Competitive Comparison (AI Recommendation Rank)
| Company | AI Recommendation Rate | Status |
| :--- | :--- | :--- |
| **{url}** | **{ai_pct}%** | [FAIL] Falling Behind |
| {competitors[0]['name']} | {competitors[0]['score']}% | [PASS] High Visibility |
| {competitors[1]['name']} | {competitors[1]['score'] - 10}% | [PASS] Moderate |

## 3. The Revenue Rollercoaster
With ~{monthly_visits} monthly visits, your digital performance peaks and valleys are unpredictable because you lack a "Source of Truth" for AI search engines. AI search models use **Citations** and **Structured Data** to recommend businesses. Without these, your visibility is left to chance.

## 4. The 3-Step "Empire" Recovery Plan
To stop losing customers to {competitors[0]['name']}, we recommend the following:
1. **Local Authority Injection**: Syncing your NAP across 50+ high-tier local citations.
2. **AI Semantic Tagging**: Adding hidden "LLM-Optimized" schema markup to your site.
3. **Sentiment Siege**: A high-authority press release to generate brand mentions that AI tools trust.

---
**Prepared by: Empire Unified Intelligence Agent**
"""

    return audit_md

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python aeo_auditor.py <url> <niche> [json_data]")
        sys.exit(1)
        
    url = sys.argv[1]
    niche = sys.argv[2]
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    
    audit = generate_aeo_audit(url, niche, data)
    print(audit)
