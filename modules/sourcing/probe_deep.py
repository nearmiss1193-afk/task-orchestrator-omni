
from playwright.sync_api import sync_playwright

URL = "https://www.floridahealthfinder.gov/facilitylocator/facloc.aspx"

def probe_deep():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"🕵️ Deep Probing {URL}...")
        page.goto(URL, timeout=30000)
        page.wait_for_load_state("networkidle")
        
        print(f"📄 Title: {page.title()}")
        print(f"📝 Text (First 200): {page.inner_text('body')[:200]}")
        
        # Check for specific buttons
        buttons = page.query_selector_all("button, input[type='submit']")
        print(f"🔘 Buttons found: {len(buttons)}")
        
        # Check iframes
        frames = page.frames
        print(f"🖼️ Frames found: {len(frames)}")
        
        # Check specific text
        if "Assisted Living" in page.content():
            print("✅ 'Assisted Living' text FOUND in HTML.")
        else:
            print("❌ 'Assisted Living' text NOT found.")

        browser.close()

if __name__ == "__main__":
    probe_deep()
