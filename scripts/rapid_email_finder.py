"""
Rapid Email Finder - Use Hunter.io to find emails for businesses
Goal: Find 10-15 verified emails by 8:30 AM
"""
import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "***REMOVED***")

def find_email_by_domain(domain: str) -> dict:
    """
    Use Hunter.io Domain Search to find emails at a company
    Returns: {email, first_name, last_name, position, confidence}
    """
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }
    
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url, params=params)
            data = response.json()
            
            if data.get("data", {}).get("emails"):
                # Get the best email (highest confidence)
                emails = data["data"]["emails"]
                best = max(emails, key=lambda x: x.get("confidence", 0))
                return {
                    "email": best.get("value"),
                    "first_name": best.get("first_name"),
                    "last_name": best.get("last_name"),
                    "position": best.get("position"),
                    "confidence": best.get("confidence"),
                    "domain": domain
                }
    except Exception as e:
        print(f"  ❌ Error for {domain}: {e}")
    
    return None


def find_email_by_name(company_name: str, domain: str = None) -> dict:
    """
    Use Hunter.io Company Search or Email Finder
    """
    # If we have a domain, use domain search
    if domain:
        return find_email_by_domain(domain)
    
    # Otherwise, try to find domain first
    url = "https://api.hunter.io/v2/domain-search"
    # Hunter doesn't support company name search directly
    # Need to derive domain from company name
    
    # Generate likely domain
    clean_name = company_name.lower().replace(" ", "").replace("'", "").replace(",", "")
    possible_domains = [
        f"{clean_name}.com",
        f"{clean_name}lakeland.com",
        f"{clean_name}fl.com"
    ]
    
    for domain in possible_domains:
        result = find_email_by_domain(domain)
        if result:
            return result
    
    return None


def check_hunter_credits():
    """Check remaining Hunter.io API credits"""
    url = "https://api.hunter.io/v2/account"
    params = {"api_key": HUNTER_API_KEY}
    
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(url, params=params)
            data = response.json()
            
            if "data" in data:
                requests = data["data"].get("requests", {})
                print(f"📊 Hunter.io Credits:")
                print(f"   Used: {requests.get('used', 0)}")
                print(f"   Available: {requests.get('available', 0)}")
                return requests.get("available", 0)
    except Exception as e:
        print(f"❌ Error checking credits: {e}")
    
    return 0


def prospect_lakeland_businesses():
    """
    Find emails for Lakeland FL businesses
    Target: Auto Repair, Roofing, HVAC
    """
    # Sample businesses to enrich (replace with real scraped data)
    businesses = [
        {"name": "ABC Roofing Lakeland", "domain": "abcroofing.com"},
        {"name": "Lakeland HVAC Pros", "domain": "lakelandhvac.com"},
        {"name": "Florida Auto Repair", "domain": "floridaautorepair.com"},
        {"name": "Polk County Plumbing", "domain": "polkcountyplumbing.com"},
        {"name": "Central Florida Landscaping", "domain": "centrallawncare.com"},
    ]
    
    print("\n" + "=" * 60)
    print("🔍 RAPID EMAIL FINDER - 8:30 AM DEADLINE")
    print("=" * 60)
    
    # Check credits first
    credits = check_hunter_credits()
    if credits < 10:
        print("⚠️ Low credits! Consider manual search instead.")
    
    results = []
    
    for biz in businesses:
        print(f"\n🏢 {biz['name']}")
        result = find_email_by_domain(biz["domain"])
        if result:
            print(f"   ✅ Found: {result['email']} ({result.get('confidence', 0)}% confidence)")
            results.append({**biz, **result})
        else:
            print(f"   ❌ No email found")
    
    print("\n" + "=" * 60)
    print(f"📈 RESULTS: {len(results)} emails found")
    print("=" * 60)
    
    for r in results:
        print(f"  • {r['name']}: {r['email']}")
    
    return results


if __name__ == "__main__":
    prospect_lakeland_businesses()
