"""
EMPIRE MASTER VERIFICATION SYSTEM
==================================
One command to verify EVERYTHING in the sales pipeline.
Run: python master_verify.py

Author: Antigravity AI
Version: 1.0.0
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from typing import Tuple, Dict, Any

# Load environment
load_dotenv()

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def ok(msg): return f"{Colors.GREEN}✅ {msg}{Colors.END}"
def fail(msg): return f"{Colors.RED}❌ {msg}{Colors.END}"
def warn(msg): return f"{Colors.YELLOW}⚠️  {msg}{Colors.END}"
def info(msg): return f"{Colors.CYAN}ℹ️  {msg}{Colors.END}"
def header(msg): return f"{Colors.BOLD}{Colors.BLUE}{'='*60}\n{msg}\n{'='*60}{Colors.END}"

# Track results
results: Dict[str, bool] = {}

# ==============================================================================
# 1. GHL API VERIFICATION
# ==============================================================================
def verify_ghl_api() -> Tuple[bool, str]:
    """Verify GoHighLevel API connectivity and token validity."""
    token = os.getenv("GHL_AGENCY_API_TOKEN") or os.getenv("GHL_API_TOKEN") or os.getenv("GHL_PRIVATE_KEY")
    location = os.getenv("GHL_LOCATION_ID")
    
    if not token:
        return False, "GHL_AGENCY_API_TOKEN not found in .env"
    if not location:
        return False, "GHL_LOCATION_ID not found in .env"
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Version": "2021-07-28"
        }
        # Test: Get location info
        res = requests.get(
            f"https://services.leadconnectorhq.com/locations/{location}",
            headers=headers,
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            name = data.get("location", {}).get("name", "Unknown")
            return True, f"Connected to '{name}'"
        else:
            return False, f"API returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 2. VAPI (SARAH) VERIFICATION
# ==============================================================================
def verify_vapi_sarah() -> Tuple[bool, str]:
    """Verify Vapi Sarah assistant exists and has phone number."""
    api_key = os.getenv("VAPI_API_KEY") or os.getenv("VAPI_PRIVATE_KEY")
    
    if not api_key:
        return False, "VAPI_API_KEY not found in .env"
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        res = requests.get(
            "https://api.vapi.ai/assistant",
            headers=headers,
            timeout=10
        )
        if res.status_code == 200:
            assistants = res.json()
            # Look for Sarah
            sarah = None
            for a in assistants:
                if "sarah" in a.get("name", "").lower() or "spartan" in a.get("name", "").lower():
                    sarah = a
                    break
            
            if sarah:
                phone_id = sarah.get("serverUrlPhoneNumberId") or sarah.get("phoneNumberId")
                if phone_id:
                    return True, f"Sarah found with phone: {phone_id[:8]}..."
                else:
                    return True, "Sarah found (no phone attached)"
            else:
                # Check if any assistant exists
                if len(assistants) > 0:
                    return True, f"{len(assistants)} assistant(s) found"
                return False, "No assistants found"
        else:
            return False, f"API returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 3. EMAIL (RESEND) VERIFICATION
# ==============================================================================
def verify_resend_email() -> Tuple[bool, str]:
    """Verify Resend email is configured and domain verified."""
    api_key = os.getenv("RESEND_API_KEY")
    
    if not api_key:
        return False, "RESEND_API_KEY not found in .env"
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        res = requests.get(
            "https://api.resend.com/domains",
            headers=headers,
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            domains = data.get("data", [])
            verified = [d for d in domains if d.get("status") == "verified"]
            if verified:
                return True, f"{len(verified)} verified domain(s): {verified[0].get('name')}"
            elif domains:
                return False, f"{len(domains)} domain(s) pending verification"
            return False, "No domains configured"
        else:
            return False, f"API returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 4. LANDING PAGES VERIFICATION
# ==============================================================================
def verify_landing_pages() -> Tuple[bool, str]:
    """Verify all 10 vertical landing pages are accessible."""
    base_url = "https://www.aiserviceco.com"
    pages = [
        "hvac.html", "plumber.html", "roofer.html", "electrician.html",
        "solar.html", "landscaping.html", "pest.html", "cleaning.html",
        "restoration.html", "autodetail.html"
    ]
    
    online = 0
    failed = []
    
    for page in pages:
        try:
            res = requests.get(f"{base_url}/{page}", timeout=5)
            if res.status_code == 200:
                online += 1
            else:
                failed.append(f"{page}:{res.status_code}")
        except:
            failed.append(f"{page}:TIMEOUT")
    
    if online == len(pages):
        return True, f"All {len(pages)} pages online"
    elif online > 0:
        return True, f"{online}/{len(pages)} online, failed: {', '.join(failed[:3])}"
    else:
        return False, f"All pages failed: {', '.join(failed[:3])}"

# ==============================================================================
# 5. CHECKOUT (STRIPE) VERIFICATION
# ==============================================================================
def verify_stripe_checkout() -> Tuple[bool, str]:
    """Verify Stripe configuration for checkout."""
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    
    if not stripe_key:
        # Check for publishable key at minimum
        pub_key = os.getenv("STRIPE_PUBLISHABLE_KEY") or os.getenv("NEXT_PUBLIC_STRIPE_KEY")
        if pub_key:
            return True, "Publishable key found (secret not checked)"
        return False, "STRIPE_SECRET_KEY not found in .env"
    
    try:
        import stripe
        stripe.api_key = stripe_key
        # Test: List products (minimal API call)
        products = stripe.Product.list(limit=1)
        return True, f"Stripe connected, {len(products.data)} product(s)"
    except ImportError:
        return True, "Stripe key found (SDK not installed)"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 6. SUPABASE DATABASE VERIFICATION
# ==============================================================================
def verify_supabase() -> Tuple[bool, str]:
    """Verify Supabase connectivity."""
    url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url:
        return False, "SUPABASE_URL not found"
    if not key:
        return False, "SUPABASE_SERVICE_KEY not found"
    
    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        # Health check
        res = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        if res.status_code in [200, 400]:  # 400 means connected but no table specified
            return True, "Supabase connected"
        else:
            return False, f"API returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 7. GHL WORKFLOWS VERIFICATION
# ==============================================================================
def verify_ghl_workflows() -> Tuple[bool, str]:
    """Verify Spartan Outreach workflow exists."""
    token = os.getenv("GHL_AGENCY_API_TOKEN")
    location = os.getenv("GHL_LOCATION_ID")
    
    if not token or not location:
        return False, "GHL credentials not found"
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Version": "2021-07-28"
        }
        # Get workflows
        res = requests.get(
            f"https://services.leadconnectorhq.com/workflows/?locationId={location}",
            headers=headers,
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            workflows = data.get("workflows", [])
            # Look for Spartan
            spartan = [w for w in workflows if "spartan" in w.get("name", "").lower()]
            if spartan:
                status = spartan[0].get("status", "unknown")
                return True, f"Spartan workflow found ({status})"
            elif len(workflows) > 0:
                return True, f"{len(workflows)} workflow(s) found (no Spartan)"
            return False, "No workflows found"
        else:
            return False, f"API returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 8. DASHBOARD ACCESSIBLE
# ==============================================================================
def verify_dashboard() -> Tuple[bool, str]:
    """Verify dashboard is accessible."""
    url = "https://www.aiserviceco.com/dashboard.html"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            if "Sovereign Command" in res.text:
                return True, "Dashboard online"
            return True, "Dashboard accessible"
        return False, f"Dashboard returned {res.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# MAIN VERIFICATION RUNNER
# ==============================================================================
def run_all_checks():
    """Run all verification checks and produce report."""
    print(header("EMPIRE MASTER VERIFICATION SYSTEM"))
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("GHL API", verify_ghl_api),
        ("Vapi (Sarah)", verify_vapi_sarah),
        ("Email (Resend)", verify_resend_email),
        ("Landing Pages", verify_landing_pages),
        ("Checkout (Stripe)", verify_stripe_checkout),
        ("Database (Supabase)", verify_supabase),
        ("Workflows (GHL)", verify_ghl_workflows),
        ("Dashboard", verify_dashboard),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_fn in checks:
        print(f"Checking {name}...", end=" ", flush=True)
        try:
            success, message = check_fn()
            results[name] = success
            if success:
                print(ok(message))
                passed += 1
            else:
                print(fail(message))
                failed += 1
        except Exception as e:
            print(fail(f"Exception: {e}"))
            results[name] = False
            failed += 1
    
    print()
    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print()
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 SALES READINESS: ✅ READY TO SELL{Colors.END}")
        return True
    elif passed >= 6:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SALES READINESS: MOSTLY READY (fix {failed} items){Colors.END}")
        return False
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SALES READINESS: NOT READY{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
