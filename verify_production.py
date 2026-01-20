#!/usr/bin/env python3
"""
Production Verifier v2 - Fetches LIVE site pages and verifies canonical numbers.
Scans: /, /hvac, /plumber, /pricing, /demo, /dashboard.html
Reports exact mismatches with expected vs found diffs.
"""
import requests
import json
import sys
import re
from datetime import datetime

CANONICAL = {
    "voice_number": "+18632132505",
    "voice_display": "(863) 213-2505",
    "voice_alt": "863-213-2505",
    "sms_number": "+13527585336",
    "sms_display": "(352) 758-5336",
    "sms_alt": "352-758-5336"
}

# Forbidden numbers - any area code that's NOT 863 or 352
FORBIDDEN_PATTERNS = [
    r"\(904\)",  # Jacksonville
    r"\(561\)",  # Palm Beach
    r"\(727\)",  # Tampa
    r"\(321\)",  # Orlando
    r"\(954\)",  # Fort Lauderdale
    r"\(305\)",  # Miami
    r"\(786\)",  # Miami
    r"\(407\)",  # Orlando
    r"\(813\)",  # Tampa
    r"695072132632677",  # Known bad number from audits
]

SITE_URL = "https://www.aiserviceco.com"
PAGES_TO_CHECK = ["/", "/hvac", "/plumber", "/pricing", "/demo", "/dashboard.html"]

def extract_phone_numbers(html):
    """Extract all phone number patterns from HTML."""
    patterns = [
        r'\+1\s*\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
        r'tel:\+?\d{10,11}',
    ]
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, html)
        found.extend(matches)
    return list(set(found))

def check_forbidden(html, url):
    """Check for forbidden number patterns."""
    issues = []
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, html):
            match = re.search(pattern, html)
            context = html[max(0, match.start()-50):match.end()+50]
            issues.append({
                "url": url,
                "pattern": pattern,
                "context": context.replace("\n", " ")[:100]
            })
    return issues

def verify_page(url, full_url):
    """Verify a single page has correct numbers."""
    result = {
        "url": full_url,
        "status": "unknown",
        "voice_found": False,
        "sms_found": False,
        "forbidden": [],
        "all_numbers": []
    }
    
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "AIServiceCo-Verifier/1.0"})
        if r.status_code == 404:
            result["status"] = "not_deployed"
            return result
        if r.status_code != 200:
            result["status"] = f"error_{r.status_code}"
            return result
        
        html = r.text
        
        # Extract all phone numbers
        result["all_numbers"] = extract_phone_numbers(html)
        
        # Check for canonical voice number
        if CANONICAL["voice_display"] in html or CANONICAL["voice_number"] in html or CANONICAL["voice_alt"] in html:
            result["voice_found"] = True
        
        # Check for canonical SMS number
        if CANONICAL["sms_display"] in html or CANONICAL["sms_number"] in html or CANONICAL["sms_alt"] in html:
            result["sms_found"] = True
        
        # Check for forbidden patterns
        result["forbidden"] = check_forbidden(html, full_url)
        
        # Determine status
        if result["forbidden"]:
            result["status"] = "forbidden_found"
        elif url == "/" and (not result["voice_found"] or not result["sms_found"]):
            result["status"] = "missing_canonical"
        else:
            result["status"] = "ok"
            
    except Exception as e:
        result["status"] = f"error: {str(e)}"
    
    return result

def check_brand_json():
    """Check /brand.json for correct canonical numbers."""
    try:
        r = requests.get(f"{SITE_URL}/brand.json", timeout=10)
        if r.status_code != 200:
            return {"status": "not_found", "error": f"HTTP {r.status_code}"}
        
        data = r.json()
        canon = data.get("canonical", {})
        
        errors = []
        if canon.get("voice_number") != CANONICAL["voice_number"]:
            errors.append(f"voice: expected {CANONICAL['voice_number']}, got {canon.get('voice_number')}")
        if canon.get("sms_number") != CANONICAL["sms_number"]:
            errors.append(f"sms: expected {CANONICAL['sms_number']}, got {canon.get('sms_number')}")
        
        return {
            "status": "ok" if not errors else "mismatch",
            "errors": errors,
            "git_sha": data.get("build", {}).get("git_sha", "unknown")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def verify_production(include_brand_audit=True):
    """Main verification function."""
    print(f"{'='*60}")
    print(f"PRODUCTION VERIFIER v2 - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    errors = []
    warnings = []
    results = []
    
    # 1. Check brand.json
    if include_brand_audit:
        print("\n1. Checking /brand.json...")
        brand_result = check_brand_json()
        if brand_result["status"] == "ok":
            print(f"   ✓ brand.json OK (git_sha: {brand_result.get('git_sha', 'unknown')})")
        elif brand_result["status"] == "not_found":
            warnings.append("brand.json not deployed")
            print(f"   ⚠ brand.json not found")
        else:
            errors.extend(brand_result.get("errors", [brand_result.get("error", "unknown")]))
            print(f"   ✗ brand.json FAILED: {brand_result}")
    
    # 2. Check all pages
    print(f"\n2. Checking {len(PAGES_TO_CHECK)} pages...")
    for page in PAGES_TO_CHECK:
        full_url = f"{SITE_URL}{page}"
        result = verify_page(page, full_url)
        results.append(result)
        
        if result["status"] == "not_deployed":
            warnings.append(f"{page} not deployed (404)")
            print(f"   ⚠ {page}: not deployed")
        elif result["status"] == "ok":
            print(f"   ✓ {page}: OK")
        elif result["status"] == "missing_canonical":
            if page == "/":
                errors.append(f"Homepage missing canonical numbers (voice={result['voice_found']}, sms={result['sms_found']})")
            print(f"   ✗ {page}: missing canonical (voice={result['voice_found']}, sms={result['sms_found']})")
        elif result["status"] == "forbidden_found":
            for f in result["forbidden"]:
                errors.append(f"FORBIDDEN number on {page}: {f['pattern']} in context: {f['context']}")
            print(f"   ✗ {page}: FORBIDDEN numbers found")
        else:
            warnings.append(f"{page}: {result['status']}")
            print(f"   ⚠ {page}: {result['status']}")
    
    # 3. Check cache status
    print("\n3. Checking cache status...")
    try:
        r = requests.head(SITE_URL, timeout=10)
        cache_status = r.headers.get("x-vercel-cache", "unknown")
        age = r.headers.get("age", "0")
        print(f"   X-Vercel-Cache: {cache_status}")
        print(f"   Age: {age}s")
        
        if cache_status == "HIT" and int(age) > 3600:
            warnings.append(f"Stale cache: Age={age}s (>1hr)")
    except:
        warnings.append("Could not check cache headers")
    
    # Report
    print(f"\n{'='*60}")
    print("VERIFICATION RESULT")
    print(f"{'='*60}")
    
    if errors:
        print(f"\n❌ FAILED - {len(errors)} error(s):")
        for e in errors:
            print(f"   • {e}")
        status = "RED"
    elif warnings:
        print(f"\n⚠️ PASSED WITH WARNINGS - {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   • {w}")
        status = "YELLOW"
    else:
        print(f"\n✅ PASSED - All canonical numbers verified")
        status = "GREEN"
    
    print(f"\nStatus: {status}")
    
    # Return structured result for programmatic use
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "pages_checked": len(results),
        "pages_ok": sum(1 for r in results if r["status"] == "ok"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = verify_production()
    if result["status"] == "RED":
        sys.exit(2)
    elif result["status"] == "YELLOW":
        sys.exit(1)
    else:
        sys.exit(0)
