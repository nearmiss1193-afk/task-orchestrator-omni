import os
import requests
import sys

URL = "https://empire-sovereign-cloud.vercel.app"
TAG = "SOV-V3.1-REBRAND-2026-02-03"

print(f"📡 Initiating Absolute Truth Verification for {URL}...")

try:
    # Use headers to bypass common cache
    headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
    r = requests.get(URL, headers=headers, timeout=15)
    
    if TAG in r.text:
        print(f"✅ VERIFIED: Found version tag '{TAG}' in live source.")
        sys.exit(0)
    else:
        print(f"❌ FAILURE: Version tag '{TAG}' NOT FOUND.")
        print("Live site is still serving legacy content.")
        sys.exit(1)
except Exception as e:
    print(f"❌ ERROR reaching site: {e}")
    sys.exit(1)
