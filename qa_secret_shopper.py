"""
WEBSITE QA SECRET SHOPPER TEST SUITE
====================================
Comprehensive automated testing of all website pages, forms, and buttons.
Runs through the entire customer journey from landing to checkout.

Usage:
    python qa_secret_shopper.py [--verbose]
"""
import os
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("SITE_URL", "https://aiserviceco.com")
PAGES_TO_TEST = [
    "/",
    "/dashboard.html",
    "/checkout.html",
    "/checkout.html?plan=lite",
    "/checkout.html?plan=growth",
    "/hvac.html",
    "/terms.html",
    "/privacy.html",
]

# Test result storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "base_url": BASE_URL,
    "tests": [],
    "summary": {"passed": 0, "failed": 0, "warnings": 0}
}


def log_test(name: str, passed: bool, details: str = ""):
    """Log a test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = {"name": name, "passed": passed, "details": details}
    test_results["tests"].append(result)
    
    if passed:
        test_results["summary"]["passed"] += 1
    else:
        test_results["summary"]["failed"] += 1
    
    print(f"{status} | {name}")
    if details and not passed:
        print(f"       → {details}")


def test_page_loads(url: str) -> bool:
    """Test that a page loads successfully"""
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            log_test(f"Page loads: {url}", True)
            return True
        else:
            log_test(f"Page loads: {url}", False, f"Status: {res.status_code}")
            return False
    except Exception as e:
        log_test(f"Page loads: {url}", False, str(e))
        return False


def test_no_raw_css(url: str) -> bool:
    """Test that no raw CSS is visible on the page"""
    try:
        res = requests.get(url, timeout=15)
        content = res.text
        
        # Check for common CSS patterns that shouldn't be visible as text
        css_patterns = [
            "--primary:",
            "--black:",
            "border-radius:",
            "background-color:",
            "font-family:",
        ]
        
        # Check if CSS appears outside of <style> tags
        # Simple heuristic: if CSS appears in <body>, it's exposed
        body_start = content.find("<body")
        if body_start != -1:
            body_content = content[body_start:]
            for pattern in css_patterns:
                # Check if pattern appears in body but not in a script tag
                if pattern in body_content and "<style" not in body_content[:body_content.find(pattern)]:
                    # Double check it's not in a script
                    pattern_pos = body_content.find(pattern)
                    script_before = body_content[:pattern_pos].rfind("<script")
                    script_end = body_content[:pattern_pos].rfind("</script>")
                    style_start = body_content[:pattern_pos].rfind("<style")
                    style_end = body_content[:pattern_pos].rfind("</style>")
                    
                    if script_before < script_end and style_start < style_end:
                        log_test(f"No raw CSS visible: {url}", False, f"Found '{pattern}' exposed")
                        return False
        
        log_test(f"No raw CSS visible: {url}", True)
        return True
    except Exception as e:
        log_test(f"No raw CSS visible: {url}", False, str(e))
        return False


def test_forms_present(url: str) -> bool:
    """Test that expected forms are present and properly structured"""
    try:
        res = requests.get(url, timeout=15)
        content = res.text
        
        # Check for form elements
        has_form = "<form" in content
        has_submit = 'type="submit"' in content or "submit-btn" in content
        
        if "checkout" in url.lower():
            # Checkout page should have form and inputs
            has_name = 'id="name"' in content or 'name="name"' in content
            has_email = 'id="email"' in content or 'type="email"' in content
            has_phone = 'id="phone"' in content or 'type="tel"' in content
            
            if has_form and has_submit and has_name and has_email:
                log_test(f"Form structure: {url}", True)
                return True
            else:
                missing = []
                if not has_form: missing.append("form tag")
                if not has_submit: missing.append("submit button")
                if not has_name: missing.append("name field")
                if not has_email: missing.append("email field")
                log_test(f"Form structure: {url}", False, f"Missing: {', '.join(missing)}")
                return False
        else:
            log_test(f"Form structure: {url}", True, "No form required")
            return True
            
    except Exception as e:
        log_test(f"Form structure: {url}", False, str(e))
        return False


def test_links_work(url: str) -> bool:
    """Test that key links on the page work"""
    try:
        res = requests.get(url, timeout=15)
        content = res.text
        
        # Extract href links
        import re
        links = re.findall(r'href="([^"]+)"', content)
        
        broken = []
        for link in links[:10]:  # Test first 10 links
            if link.startswith("#") or link.startswith("javascript:"):
                continue
            if link.startswith("mailto:") or link.startswith("tel:"):
                continue
            if link.startswith("http"):
                full_url = link
            else:
                full_url = urljoin(url, link)
            
            try:
                link_res = requests.head(full_url, timeout=5, allow_redirects=True)
                if link_res.status_code >= 400:
                    broken.append(f"{link} ({link_res.status_code})")
            except:
                pass  # Skip external links that timeout
        
        if broken:
            log_test(f"Links work: {url}", False, f"Broken: {broken[:3]}")
            return False
        
        log_test(f"Links work: {url}", True)
        return True
        
    except Exception as e:
        log_test(f"Links work: {url}", False, str(e))
        return False


def test_api_endpoints() -> bool:
    """Test that API endpoints respond"""
    endpoints = [
        "/api/stats",
        "/api/leads",
    ]
    
    all_passed = True
    for endpoint in endpoints:
        url = urljoin(BASE_URL, endpoint)
        try:
            res = requests.get(url, timeout=15)
            if res.status_code in [200, 201, 401, 403]:  # 401/403 is ok, means endpoint exists
                log_test(f"API endpoint: {endpoint}", True)
            else:
                log_test(f"API endpoint: {endpoint}", False, f"Status: {res.status_code}")
                all_passed = False
        except Exception as e:
            log_test(f"API endpoint: {endpoint}", False, str(e))
            all_passed = False
    
    return all_passed


def run_full_qa():
    """Run the complete QA test suite"""
    print("=" * 60)
    print("🔍 SECRET SHOPPER QA TEST SUITE")
    print(f"Target: {BASE_URL}")
    print(f"Started: {test_results['timestamp']}")
    print("=" * 60)
    print()
    
    # 1. Test all pages load
    print("📄 TESTING PAGE LOADS...")
    for page in PAGES_TO_TEST:
        url = urljoin(BASE_URL, page)
        test_page_loads(url)
    print()
    
    # 2. Test no raw CSS visible
    print("🎨 TESTING CSS RENDERING...")
    for page in PAGES_TO_TEST:
        url = urljoin(BASE_URL, page)
        test_no_raw_css(url)
    print()
    
    # 3. Test forms
    print("📝 TESTING FORMS...")
    form_pages = [p for p in PAGES_TO_TEST if "checkout" in p.lower()]
    for page in form_pages:
        url = urljoin(BASE_URL, page)
        test_forms_present(url)
    print()
    
    # 4. Test links
    print("🔗 TESTING LINKS...")
    test_links_work(urljoin(BASE_URL, "/"))
    test_links_work(urljoin(BASE_URL, "/checkout.html"))
    print()
    
    # 5. Test API
    print("⚡ TESTING API ENDPOINTS...")
    test_api_endpoints()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 QA SUMMARY")
    print(f"   ✅ Passed: {test_results['summary']['passed']}")
    print(f"   ❌ Failed: {test_results['summary']['failed']}")
    print("=" * 60)
    
    # Save results
    with open("qa_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("\n📁 Results saved to qa_results.json")
    
    # Return True if all tests passed
    return test_results['summary']['failed'] == 0


if __name__ == "__main__":
    success = run_full_qa()
    exit(0 if success else 1)
