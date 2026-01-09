"""
PRE-FLIGHT LINK CHECKER
=======================
Validates all URLs in campaign emails/pages before sending.
Catches dead links, 404s, and slow responses BEFORE they reach prospects.

Usage:
    from modules.preflight_checker import validate_campaign_links
    
    issues = validate_campaign_links(email_html)
    if issues:
        print("BLOCKED: Fix these links first")
"""
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from datetime import datetime

# Default timeout for link checks
TIMEOUT = 5

# Known good domains (skip checking these for speed)
TRUSTED_DOMAINS = [
    "aiserviceco.com",
    "www.aiserviceco.com",
    "app.gohighlevel.com",
    "dashboard.vapi.ai",
    "supabase.com"
]


def extract_urls(content: str) -> list:
    """Extract all URLs from HTML/text content."""
    url_pattern = r'https?://[^\s<>"\']+[^\s<>"\',.]'
    urls = re.findall(url_pattern, content)
    # Clean trailing characters
    cleaned = []
    for url in urls:
        url = url.rstrip(')')
        if url not in cleaned:
            cleaned.append(url)
    return cleaned


def check_url(url: str) -> dict:
    """Check a single URL for accessibility."""
    result = {
        "url": url,
        "status": None,
        "ok": False,
        "error": None,
        "response_time_ms": None
    }
    
    # Skip trusted domains (optional)
    domain = urlparse(url).netloc
    
    try:
        start = datetime.now()
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        result["status"] = response.status_code
        result["response_time_ms"] = round(elapsed, 2)
        result["ok"] = response.status_code < 400
        
        if not result["ok"]:
            result["error"] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection failed"
    except Exception as e:
        result["error"] = str(e)[:50]
    
    return result


def validate_campaign_links(content: str, verbose: bool = True) -> list:
    """
    Validate all links in campaign content.
    
    Returns list of problematic links (empty = all good!)
    """
    urls = extract_urls(content)
    
    if verbose:
        print(f"[PREFLIGHT] Checking {len(urls)} URLs...")
    
    issues = []
    
    # Check URLs in parallel for speed
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        
        for future in as_completed(futures):
            result = future.result()
            
            if not result["ok"]:
                issues.append(result)
                if verbose:
                    print(f"  ❌ {result['url']}: {result['error']}")
            elif verbose:
                print(f"  ✅ {result['url']} ({result['response_time_ms']}ms)")
    
    if verbose:
        if issues:
            print(f"\n[PREFLIGHT] ⚠️  BLOCKED: {len(issues)} broken links found!")
        else:
            print(f"\n[PREFLIGHT] ✅ All {len(urls)} links OK!")
    
    return issues


def preflight_email(email_html: str) -> bool:
    """
    Pre-flight check for email content.
    Returns True if OK to send, False if blocked.
    """
    issues = validate_campaign_links(email_html)
    return len(issues) == 0


def preflight_campaign_file(filepath: str) -> bool:
    """Check all links in a Python campaign file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"[PREFLIGHT] Scanning: {filepath}")
    issues = validate_campaign_links(content)
    return len(issues) == 0


if __name__ == "__main__":
    # Test the checker
    test_html = """
    <a href="https://www.aiserviceco.com/features.html">Good Link</a>
    <a href="https://calendly.com/aiserviceco/demo">Bad Link</a>
    <a href="https://www.aiserviceco.com/dashboard.html">Dashboard</a>
    """
    
    print("=" * 60)
    print("PRE-FLIGHT LINK CHECKER TEST")
    print("=" * 60)
    
    issues = validate_campaign_links(test_html)
    
    print("\n" + "=" * 60)
    if issues:
        print("RESULT: BLOCKED - Fix broken links before sending!")
    else:
        print("RESULT: PASSED - Safe to send!")
    print("=" * 60)
