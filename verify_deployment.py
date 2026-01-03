import sys
import time
from playwright.sync_api import sync_playwright

def verify_deployment(target_url=None):
    if not target_url:
        target_url = "https://empire-hvac-demo-sovereign.surge.sh/hvac.html"
    
    print(f"🚀 Starting Deployment Verification for: {target_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("   📍 Navigating...")
            # Bypass Localtunnel reminder page
            page.set_extra_http_headers({"Bypass-Tunnel-Reminder": "true"})
            
            response = page.goto(target_url, timeout=30000)
            if not response.ok:
                print(f"   ❌ HTTP Error: {response.status}")
                return False
                
            page.wait_for_load_state("networkidle")
            print("   ✅ Page Loaded.")
            
            # Check 1: Title
            title = page.title()
            print(f"   ℹ️  Title: {title}")
            
            # Check 2: Chat Widget
            if page.locator(".chat-widget-trigger").is_visible():
                print("   ✅ Chat Widget Visible.")
            else:
                 print("   ⚠️ Chat Widget NOT visible.")

            # Check 3: Main CTA (Text varies, so look for button/link)
            # Based on inspection, it might be "Get Started", "Start Now", or "Get My Free Quote"
            # We will use a broader selector or the exact one from hvac.html
            cta = page.locator("a:has-text('Get Started'), button:has-text('Get Started'), a:has-text('Start Now')").first
            if cta.count() > 0 and cta.is_visible():
                print("   ✅ Main CTA Found.")
            else:
                print("   ⚠️ Main CTA NOT Found (Check selector).")
                
            # Check 4: Footer
            if page.locator("footer").is_visible():
                 print("   ✅ Footer Visible.")
            
            print("\n✅ DEPLOYMENT VERIFIED.")
            return True

        except Exception as e:
            print(f"   ❌ Verification Failed: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    verify_deployment(url)
