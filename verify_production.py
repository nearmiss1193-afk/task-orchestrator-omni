#!/usr/bin/env python3
"""
Production Verifier - Fetches live site and /brand.json, verifies canonical numbers match.
Run after each deploy to confirm website truth.
"""
import requests
import json
import sys
from datetime import datetime

CANONICAL = {
    "voice_number": "+18632132505",
    "voice_display": "(863) 213-2505",
    "sms_number": "+13527585336",
    "sms_display": "(352) 758-5336"
}

SITE_URL = "https://www.aiserviceco.com"

def verify_production():
    print(f"{'='*60}")
    print(f"PRODUCTION VERIFIER - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    errors = []
    warnings = []
    
    # 1. Fetch /brand.json
    print("\n1. Checking /brand.json...")
    try:
        r = requests.get(f"{SITE_URL}/brand.json", timeout=15)
        if r.status_code == 200:
            brand = r.json()
            print(f"   ✓ brand.json found (git_sha: {brand.get('build', {}).get('git_sha', 'unknown')})")
            
            # Verify canonical numbers match
            canon = brand.get("canonical", {})
            if canon.get("voice_number") != CANONICAL["voice_number"]:
                errors.append(f"brand.json voice_number mismatch: {canon.get('voice_number')}")
            if canon.get("sms_number") != CANONICAL["sms_number"]:
                errors.append(f"brand.json sms_number mismatch: {canon.get('sms_number')}")
        else:
            warnings.append(f"/brand.json not found (status {r.status_code})")
    except Exception as e:
        warnings.append(f"Failed to fetch /brand.json: {e}")
    
    # 2. Fetch homepage and check for numbers
    print("\n2. Checking homepage HTML...")
    try:
        r = requests.get(SITE_URL, timeout=15)
        if r.status_code == 200:
            html = r.text
            
            # Check voice number
            if CANONICAL["voice_display"] in html or CANONICAL["voice_number"] in html:
                print(f"   ✓ Voice number found on page")
            else:
                errors.append(f"Voice number {CANONICAL['voice_display']} NOT found on homepage")
            
            # Check SMS number
            if CANONICAL["sms_display"] in html or CANONICAL["sms_number"] in html:
                print(f"   ✓ SMS number found on page")
            else:
                errors.append(f"SMS number {CANONICAL['sms_display']} NOT found on homepage")
            
            # Check for wrong numbers (common mistakes)
            wrong_numbers = ["(904)", "(561)", "(727)", "(321)"]
            for wrong in wrong_numbers:
                if wrong in html:
                    errors.append(f"WRONG number found on page: {wrong}")
        else:
            errors.append(f"Homepage returned {r.status_code}")
    except Exception as e:
        errors.append(f"Failed to fetch homepage: {e}")
    
    # 3. Check cache headers
    print("\n3. Checking cache status...")
    try:
        r = requests.head(SITE_URL, timeout=10)
        cache_status = r.headers.get("x-vercel-cache", "unknown")
        age = r.headers.get("age", "0")
        print(f"   X-Vercel-Cache: {cache_status}")
        print(f"   Age: {age}s")
        
        if cache_status == "HIT" and int(age) > 3600:
            warnings.append(f"Stale cache: Age={age}s (>1hr)")
    except Exception as e:
        warnings.append(f"Failed to check headers: {e}")
    
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
    return 0 if status == "GREEN" else (1 if status == "YELLOW" else 2)

if __name__ == "__main__":
    sys.exit(verify_production())
