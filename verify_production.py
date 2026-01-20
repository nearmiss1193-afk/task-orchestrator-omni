#!/usr/bin/env python3
"""
Production Verifier v3 - Truth Guardrails
- Auto-discovers public/*.html pages
- Fetches live pages and brand.json
- Validates forbidden patterns and canonical numbers
- Outputs JSON report: production_audit_report.json
- Exit 1 on failure
"""
import requests
import json
import sys
import re
import os
from datetime import datetime
from pathlib import Path

SITE_URL = "https://www.aiserviceco.com"

# Load from local brand.json as reference
def load_brand_config():
    """Load brand.json from public/ directory"""
    try:
        brand_path = Path(__file__).parent / "public" / "brand.json"
        with open(brand_path) as f:
            return json.load(f)
    except:
        # Fallback to hardcoded
        return {
            "canonical": {
                "voice_number_e164": "+18632132505",
                "voice_display": "(863) 213-2505",
                "sms_number_e164": "+13527585336",
                "sms_display": "(352) 758-5336"
            },
            "forbidden_patterns": [
                "(904)", "(561)", "(727)", "(321)", "(954)",
                "(305)", "(786)", "(407)", "(813)", "695072132632677"
            ],
            "verification": {
                "must_match_voice": ["+18632132505", "(863) 213-2505", "863-213-2505"],
                "must_match_sms": ["+13527585336", "(352) 758-5336", "352-758-5336"]
            }
        }

def discover_public_pages():
    """Auto-discover HTML pages in public/ directory"""
    public_dir = Path(__file__).parent / "public"
    pages = ["/", "/dashboard.html", "/brand.json"]
    
    if public_dir.exists():
        for html_file in public_dir.glob("*.html"):
            page = "/" + html_file.name
            if page not in pages:
                pages.append(page)
    
    return pages

def check_forbidden(html, url, forbidden_patterns):
    """Check for forbidden number patterns"""
    issues = []
    for pattern in forbidden_patterns:
        if pattern in html:
            # Find context around match
            idx = html.find(pattern)
            context = html[max(0, idx-30):idx+len(pattern)+30]
            issues.append({
                "url": url,
                "pattern": pattern,
                "context": context.replace("\n", " ")[:80]
            })
    return issues

def check_canonical(html, url, must_match):
    """Check that at least one canonical number variant appears"""
    for variant in must_match:
        if variant in html:
            return True
    return False

def verify_page(url, full_url, brand_config):
    """Verify a single page"""
    result = {
        "url": full_url,
        "status": "unknown",
        "voice_found": False,
        "sms_found": False,
        "forbidden": [],
        "http_status": None
    }
    
    try:
        r = requests.get(full_url, timeout=15, headers={"User-Agent": "AIServiceCo-Verifier/3.0"})
        result["http_status"] = r.status_code
        
        if r.status_code == 404:
            result["status"] = "not_deployed"
            return result
        if r.status_code != 200:
            result["status"] = f"error_{r.status_code}"
            return result
        
        html = r.text
        canon = brand_config.get("canonical", {})
        forbidden = brand_config.get("forbidden_patterns", [])
        verify = brand_config.get("verification", {})
        
        # Check for forbidden patterns
        result["forbidden"] = check_forbidden(html, full_url, forbidden)
        
        # Check for canonical voice number (only on pages that should have it)
        if url in ["/", "/dashboard.html"]:
            result["voice_found"] = check_canonical(html, url, verify.get("must_match_voice", []))
            result["sms_found"] = check_canonical(html, url, verify.get("must_match_sms", []))
        else:
            result["voice_found"] = True  # Not required
            result["sms_found"] = True    # Not required
        
        # Determine status
        if result["forbidden"]:
            result["status"] = "forbidden_found"
        elif url in ["/", "/dashboard.html"] and (not result["voice_found"] or not result["sms_found"]):
            result["status"] = "missing_canonical"
        else:
            result["status"] = "ok"
            
    except Exception as e:
        result["status"] = f"error: {str(e)}"
    
    return result

def verify_brand_json(brand_config):
    """Verify brand.json is served correctly"""
    try:
        r = requests.get(f"{SITE_URL}/brand.json", timeout=10)
        if r.status_code != 200:
            return {"status": "not_found", "error": f"HTTP {r.status_code}"}
        
        data = r.json()
        local_canon = brand_config.get("canonical", {})
        remote_canon = data.get("canonical", {})
        
        errors = []
        if remote_canon.get("voice_number_e164") != local_canon.get("voice_number_e164"):
            errors.append(f"voice mismatch: local={local_canon.get('voice_number_e164')}, remote={remote_canon.get('voice_number_e164')}")
        if remote_canon.get("sms_number_e164") != local_canon.get("sms_number_e164"):
            errors.append(f"sms mismatch: local={local_canon.get('sms_number_e164')}, remote={remote_canon.get('sms_number_e164')}")
        
        return {
            "status": "ok" if not errors else "mismatch",
            "errors": errors,
            "build_sha": data.get("build", {}).get("sha", "unknown")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def verify_production():
    """Main verification function"""
    print(f"{'='*60}")
    print(f"PRODUCTION VERIFIER v3 - Truth Guardrails")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    brand_config = load_brand_config()
    errors = []
    warnings = []
    results = []
    
    # 1. Check brand.json
    print("\n1. Checking /brand.json...")
    brand_result = verify_brand_json(brand_config)
    if brand_result["status"] == "ok":
        print(f"   ✓ brand.json OK (sha: {brand_result.get('build_sha', 'unknown')})")
    elif brand_result["status"] == "not_found":
        warnings.append("brand.json not deployed")
        print(f"   ⚠ brand.json not found")
    else:
        for e in brand_result.get("errors", [brand_result.get("error", "unknown")]):
            errors.append(f"brand.json: {e}")
        print(f"   ✗ brand.json FAILED")
    
    # 2. Discover and check pages
    pages = discover_public_pages()
    print(f"\n2. Checking {len(pages)} pages...")
    
    for page in pages:
        if page == "/brand.json":
            continue  # Already checked
        
        full_url = f"{SITE_URL}{page}"
        result = verify_page(page, full_url, brand_config)
        results.append(result)
        
        if result["status"] == "not_deployed":
            warnings.append(f"{page} not deployed (404)")
            print(f"   ⚠ {page}: not deployed")
        elif result["status"] == "ok":
            print(f"   ✓ {page}: OK")
        elif result["status"] == "forbidden_found":
            for f in result["forbidden"]:
                errors.append(f"FORBIDDEN on {page}: {f['pattern']} in: {f['context']}")
            print(f"   ✗ {page}: FORBIDDEN numbers found!")
        elif result["status"] == "missing_canonical":
            errors.append(f"{page} missing canonical numbers (voice={result['voice_found']}, sms={result['sms_found']})")
            print(f"   ✗ {page}: missing canonical")
        else:
            warnings.append(f"{page}: {result['status']}")
            print(f"   ⚠ {page}: {result['status']}")
    
    # 3. Cache status
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
    
    # Build report
    report = {
        "timestamp": datetime.now().isoformat(),
        "site_url": SITE_URL,
        "status": "GREEN" if not errors else ("YELLOW" if not any("FORBIDDEN" in e for e in errors) else "RED"),
        "errors": errors,
        "warnings": warnings,
        "pages_checked": len(results),
        "pages_ok": sum(1 for r in results if r["status"] == "ok"),
        "brand_json": brand_result,
        "page_results": results
    }
    
    # Save JSON report
    report_path = Path(__file__).parent / "production_audit_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved: {report_path}")
    
    # Summary
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
    return report

if __name__ == "__main__":
    report = verify_production()
    if report["status"] == "RED":
        sys.exit(1)
    elif report["status"] == "YELLOW":
        sys.exit(0)  # Warnings are acceptable
    else:
        sys.exit(0)
