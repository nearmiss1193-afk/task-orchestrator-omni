"""
Automated Smoke Tests - API + Health Checks
Verifies live endpoints are responding correctly after deploy.
Run: python tests/smoke_test.py
"""
import requests
import sys
import argparse

ENDPOINTS = {
    "modal_health": "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health",
    "modal_optimize": "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/optimize",
    "cloudflare_webhook": "https://empire-webhook-fallback.workers.dev",
}

def test_health(base_url=None):
    url = f"{base_url}/health" if base_url else ENDPOINTS["modal_health"]
    r = requests.get(url, timeout=10)
    assert r.status_code == 200, f"Health endpoint failed: {r.status_code}"
    print("✔ Modal health OK")

def test_optimize(base_url=None):
    url = f"{base_url}/optimize" if base_url else ENDPOINTS["modal_optimize"]
    r = requests.get(url, timeout=10)
    assert r.status_code == 200, f"Optimize endpoint failed: {r.status_code}"
    print("✔ Modal optimize OK")

def test_cloudflare_webhook():
    r = requests.post(ENDPOINTS["cloudflare_webhook"], json={"test": True}, timeout=10)
    assert r.status_code == 200, f"Cloudflare webhook failed: {r.status_code}"
    print("✔ Cloudflare webhook OK")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="Override base URL for canary testing")
    args = parser.parse_args()
    
    try:
        test_health(args.base_url)
        test_optimize(args.base_url)
        test_cloudflare_webhook()
        print("✅ ALL TESTS PASS")
    except AssertionError as e:
        print("❌ TEST FAILURE:", e)
        sys.exit(1)
