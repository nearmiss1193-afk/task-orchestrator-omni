
from playwright.sync_api import sync_playwright
import time

URL = "https://www.floridahealthfinder.gov/facilitylocator/facilitysearch.aspx"

def probe():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"🕵️ Visiting {URL}...")
        try:
            page.goto(URL, timeout=30000)
        except:
            # Fallback to general locator if specific search URL fails
            fallback = "https://www.floridahealthfinder.gov/facilitylocator/facloc.aspx"
            print(f"⚠️ Redirecting to Fallback: {fallback}")
            page.goto(fallback)

        print(f"📄 Title: {page.title()}")
        
        # Screenshot
        page.screenshot(path="alf_probe.png")
        print("📸 Screenshot saved to alf_probe.png")
        
        # List Selects
        selects = page.query_selector_all("select")
        print(f"found {len(selects)} dropdowns.")
        
        for i, s in enumerate(selects):
            name = s.get_attribute("name")
            id_val = s.get_attribute("id")
            print(f"Dropdown {i}: ID='{id_val}' Name='{name}'")
            
            # Print first 5 options
            options = s.query_selector_all("option")
            for j, opt in enumerate(options[:5]):
                print(f"  - {opt.text_content().strip()} (val={opt.get_attribute('value')})")

        browser.close()

if __name__ == "__main__":
    probe()
