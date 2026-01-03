
from playwright.sync_api import sync_playwright
import time
import sys

# Base format
BASE_URL = "http://localhost:3000/landing/{}.html"

LANDING_PAGES = [
    {"name": "hvac-landing", "check": "Cooling Cal"},
    {"name": "plumber-landing", "check": "Dispatch Dan"},
    {"name": "roofer-landing", "check": "Estimator Eric"},
    # We test a sample of them to ensure the system is up
]

def verify_with_playwright():
    print("🕵️ Starting Sovereign Landing Page Verification (Playwright)...")
    
    with sync_playwright() as p:
        # Use a real browser context
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        passed = 0
        
        for site in LANDING_PAGES:
            url = BASE_URL.format(site['name'])
            check_text = site['check']
            
            print(f"   Navigating to {url}...", end=" ")
            try:
                page = context.new_page()
                page.goto(url, timeout=30000)
                
                # Check for specific text content (Vapi script trigger or Title)
                # Since Vapi is loaded via JS, we check page content
                content = page.content()
                
                if "AI Service Co" in content or "80% of Businesses Fail" in content:
                    print("✅ LOADED.")
                    passed += 1
                else:
                    print(f"❌ CONTENT MISMATCH. (Didn't find 'AI Service Co')")
                    
                page.close()
            except Exception as e:
                print(f"❌ ERROR: {e}")
                
        browser.close()
        
        if passed == len(LANDING_PAGES):
            print("\n🎉 All Verified Sites are ONLINE.")
            sys.exit(0)
        else:
            print(f"\n⚠️ Verification Incomplete: {passed}/{len(LANDING_PAGES)} passed.")
            sys.exit(1)

if __name__ == "__main__":
    verify_with_playwright()
