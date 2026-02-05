"""
Simple website testing - no API rate limits.
Tests: response time, SSL, HTTP status, redirects.

// turbo-all
"""
import json
import time
import requests
from urllib.parse import urlparse

def test_website(url: str) -> dict:
    """Test website for basic performance and security issues"""
    
    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url
    
    result = {
        "url": url,
        "status": None,
        "response_time_ms": None,
        "has_ssl": "https" in url,
        "ssl_valid": False,
        "redirects": 0,
        "error": None
    }
    
    try:
        # Test HTTPS first
        start = time.time()
        resp = requests.get(url, timeout=15, allow_redirects=True)
        end = time.time()
        
        result["status"] = resp.status_code
        result["response_time_ms"] = int((end - start) * 1000)
        result["redirects"] = len(resp.history)
        result["ssl_valid"] = url.startswith("https") and resp.ok
        result["final_url"] = resp.url
        
        # Determine status
        load_time = result["response_time_ms"]
        if load_time < 2000:
            result["speed_rating"] = "GOOD"
        elif load_time < 5000:
            result["speed_rating"] = "SLOW"
        else:
            result["speed_rating"] = "CRITICAL"
        
        # Check for HTTPS
        if not url.startswith("https"):
            try:
                https_url = url.replace("http://", "https://")
                https_resp = requests.get(https_url, timeout=5)
                result["has_https"] = https_resp.ok
            except:
                result["has_https"] = False
        else:
            result["has_https"] = True
        
    except requests.exceptions.SSLError:
        result["error"] = "SSL certificate error"
        result["ssl_valid"] = False
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection failed"
    except requests.exceptions.Timeout:
        result["error"] = "Timeout (>15s)"
        result["speed_rating"] = "CRITICAL"
    except Exception as e:
        result["error"] = str(e)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("WEBSITE TESTING - Quick Performance Check")
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
        
        print(f"\n{company}...")
        result = test_website(website)
        result["company_name"] = company
        result["email"] = p.get("email")
        result["phone"] = p.get("phone")
        result["industry"] = p.get("industry")
        result["city"] = p.get("city")
        
        if result["error"]:
            print(f"  ❌ {result['error']}")
        else:
            rating = result.get("speed_rating", "?")
            icon = "🟢" if rating == "GOOD" else ("🟡" if rating == "SLOW" else "🔴")
            print(f"  {icon} {result['response_time_ms']}ms | Status: {result['status']} | SSL: {'✓' if result['ssl_valid'] else '✗'}")
        
        results.append(result)
    
    # Save results
    with open("website_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    good = [r for r in results if r.get("speed_rating") == "GOOD"]
    slow = [r for r in results if r.get("speed_rating") == "SLOW"]
    critical = [r for r in results if r.get("speed_rating") == "CRITICAL" or r.get("error")]
    
    print(f"\n🟢 GOOD (<2s): {len(good)}")
    print(f"🟡 SLOW (2-5s): {len(slow)}")
    print(f"🔴 CRITICAL (>5s or error): {len(critical)}")
    
    if critical:
        print("\n🔴 CRITICAL - Best outreach targets:")
        for r in critical:
            err = r.get('error')
            if err:
                print(f"  {r['company_name']}: {err}")
            else:
                print(f"  {r['company_name']}: {r['response_time_ms']}ms")
    
    print(f"\nResults saved to website_test_results.json")

