import os
import time
from playwright.sync_api import sync_playwright

class GHLProspector:
    """
    Automates the generation of Deficiency Reports via GoHighLevel's Prospecting Tool.
    """
    
    def __init__(self, email=None, password=None, headless=True):
        self.email = email or os.getenv("GHL_EMAIL")
        self.password = password or os.getenv("GHL_PASSWORD")
        self.headless = headless
        self.prospecting_url = "https://app.gohighlevel.com/prospecting"

    def generate_report(self, business_name, city_state):
        """
        Generates a report for a specific business and returns the Share Link.
        """
        print(f"🕵️ [GHL PROSPECTOR] Starting Audit for: {business_name} ({city_state})")
        
        with sync_playwright() as p:
            # Launch Browser
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
            
            try:
                # 1. Login
                print("   🔑 Logging in...")
                page.goto("https://app.gohighlevel.com/", timeout=60000)
                
                # Check if already logged in or need credentials
                if page.locator("input[type='email']").is_visible():
                    page.fill("input[type='email']", self.email)
                    page.fill("input[type='password']", self.password)
                    page.click("button:has-text('Sign in')")
                    page.wait_for_url("**/dashboard", timeout=60000)
                
                print("   ✅ Login success.")
                
                # 2. Go to Prospecting
                print("   🧭 Navigating to Prospecting Tool...")
                page.goto(self.prospecting_url, timeout=60000)
                page.wait_for_selector("button:has-text('Add Prospect')", timeout=30000)
                
                # 3. Add Prospect
                print("   ➕ Adding Prospect...")
                page.click("button:has-text('Add Prospect')")
                
                # Wait for modal/input
                # NOTE: Selectors are estimates based on standard UI libraries GHL uses. 
                # May need adjustment during live debug.
                page.wait_for_selector("input[placeholder*='Business Name'], input[type='text']")
                page.fill("input[placeholder*='Business Name'], input[type='text']", f"{business_name} {city_state}")
                
                # Wait for autocomplete results
                time.sleep(3) 
                # Click the first result if it appears
                page.locator(".pac-item, .google-places-result, li[role='option']").first.click()
                
                page.wait_for_timeout(2000)

                # Confirm generation
                # Usually a primary button like "Generate Report" or "Save"
                save_btn = page.locator("button:has-text('Generate Report'), button:has-text('Save Prospect')").first
                if save_btn.is_visible():
                    save_btn.click()
                
                # 4. Wait for Report Generation
                print("   ⏳ Generating Report (this takes ~30s)...")
                # Look for a "View Report" button or similar success state
                # GHL might redirect to the report page or show a listing
                page.wait_for_selector("text=View Report", timeout=60000)
                
                # 5. Extract Share Link
                print("   🔗 Extracting Share Link...")
                # Usually there's a "Share" button that copies to clipboard or shows a modal
                # For this v1, let's try to find the "View Report" link which might be the share link 
                # or lead to the page where we can get it.
                
                # Click View Report to open it
                page.click("text=View Report")
                time.sleep(5) # Wait for report to load
                
                # Check URL
                current_url = page.url
                if "analyzemy.business" in current_url:
                    share_link = current_url
                else:
                    # Look for Share Button inside the iframe or page
                    page.click("button:has-text('Share')")
                    share_link = page.locator("input[readonly]").input_value()
                
                print(f"   🎉 SUCCESS: {share_link}")
                return share_link
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                # debug screenshot
                page.screenshot(path=f"ghl_error_{int(time.time())}.png")
                return None
            finally:
                browser.close()

if __name__ == "__main__":
    # Test Run
    prospector = GHLProspector(headless=False) # Run headed to see what happens
    link = prospector.generate_report("ProCare Lakeland HVAC Repair", "Lakeland, FL")
    print(f"Result: {link}")
