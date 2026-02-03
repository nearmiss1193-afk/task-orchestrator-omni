
from playwright.sync_api import sync_playwright

URL = "https://www.floridahealthfinder.gov/facilitylocator/facloc.aspx"

def analyze():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"🕵️ Analyzing {URL}...")
        page.goto(URL, timeout=60000)
        
        with open("page_layout.txt", "w", encoding="utf-8") as f:
            f.write(f"TITLE: {page.title()}\n")
            
            # Selects
            selects = page.query_selector_all("select")
            f.write(f"\nSELECTS ({len(selects)}):\n")
            for s in selects:
                name = s.get_attribute("name")
                id_val = s.get_attribute("id")
                f.write(f"  - ID: {id_val} | Name: {name}\n")
                # Options
                opts = s.query_selector_all("option")
                for o in opts[:10]: # First 10
                    f.write(f"      [ ] {o.text_content().strip()} (val={o.get_attribute('value')})\n")

            # Inputs
            inputs = page.query_selector_all("input")
            f.write(f"\nINPUTS ({len(inputs)}):\n")
            for i in inputs:
                typ = i.get_attribute("type")
                val = i.get_attribute("value")
                if typ in ["submit", "button", "text"]:
                    f.write(f"  - Type: {typ} | Value: {val} | ID: {i.get_attribute('id')}\n")

        browser.close()
        print("✅ Analysis saved to page_layout.txt")

if __name__ == "__main__":
    analyze()
