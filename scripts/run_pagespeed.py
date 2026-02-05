"""
Run PageSpeed tests with rate limiting.
Test websites and collect REAL metrics for email outreach.

// turbo-all
"""
import json
import time
import requests

PSI_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def test_website(url: str) -> dict:
    """Run PageSpeed test with retry on rate limit"""
    
    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url
    
    print(f"\n  Testing: {url}")
    
    for attempt in range(3):
        try:
            params = {
                "url": url,
                "strategy": "mobile"
            }
            resp = requests.get(PSI_API, params=params, timeout=60)
            
            if resp.status_code == 429:
                wait_time = 10 * (attempt + 1)
                print(f"    Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}", "url": url}
            
            data = resp.json()
            lh = data.get("lighthouseResult", {})
            audits = lh.get("audits", {})
            cats = lh.get("categories", {})
            
            result = {
                "url": url,
                "performance_score": int(cats.get("performance", {}).get("score", 0) * 100),
                "seo_score": int(cats.get("seo", {}).get("score", 0) * 100),
                "first_contentful_paint": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
                "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                "speed_index": audits.get("speed-index", {}).get("displayValue", "N/A"),
                "total_blocking_time": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
            }
            
            score = result["performance_score"]
            if score >= 90:
                status = "🟢 EXCELLENT"
            elif score >= 50:
                status = "🟡 NEEDS WORK"
            else:
                status = "🔴 CRITICAL"
            
            print(f"    {status} Performance: {score}/100 | LCP: {result['largest_contentful_paint']}")
            return result
            
        except Exception as e:
            print(f"    Error: {e}")
            return {"error": str(e), "url": url}
    
    return {"error": "Rate limited after 3 attempts", "url": url}


if __name__ == "__main__":
    print("=" * 70)
    print("PAGESPEED TESTING - Real Website Metrics")
    print("=" * 70)
    
    # Load prospects
    with open("prospects_ready.json", "r") as f:
        prospects = json.load(f)
    
    results = []
    
    for p in prospects:
        company = p.get("company_name", "Unknown")
        website = p.get("website", "")
        
        if not website:
            continue
        
        print(f"\n{company}:")
        result = test_website(website)
        result["company_name"] = company
        result["email"] = p.get("email")
        result["phone"] = p.get("phone")
        result["industry"] = p.get("industry")
        result["city"] = p.get("city")
        results.append(result)
        
        # Rate limit delay
        time.sleep(3)
    
    # Save results
    with open("pagespeed_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    success = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    
    print(f"\nSuccessful tests: {len(success)}")
    print(f"Failed tests: {len(failed)}")
    
    if success:
        print("\n✅ Websites tested successfully:")
        for r in success:
            print(f"  {r['company_name']}: {r['performance_score']}/100 Performance")
    
    if failed:
        print("\n❌ Failed tests:")
        for r in failed:
            print(f"  {r['company_name']}: {r['error']}")
    
    print(f"\nResults saved to pagespeed_results.json")
