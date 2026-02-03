
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os

URL = "https://www.floridahealthfinder.gov/facilitylocator/facloc.aspx"
OUTPUT_FILE = "facilities_list.csv"

def scrape_alf():
    print("🏥 Starting ALF Scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = context.new_page()
        
        try:
            print(f"👉 Navigating to {URL}...")
            page.goto(URL, timeout=60000)
            
            # 1. Handle potential Disclaimer (often just a Search button on first load)
            # Try to find "Facility Type" dropdown directly
            try:
                print("🔎 Looking for Facility Type dropdown...")
                # ASP.NET ID is complex, try by name or label
                page.wait_for_selector("select", timeout=5000)
                
                # Iterate dropdowns to find the one with "Assisted Living Facilities"
                selects = page.query_selector_all("select")
                target_select = None
                
                for s in selects:
                    text = s.text_content()
                    if "Assisted Living Facilities" in text:
                        target_select = s
                        print(f"✅ Found Facility Type Dropdown: {s.get_attribute('name')}")
                        break
                
                if target_select:
                    # Select "Assisted Living Facilities"
                    # We need the value.
                    options = target_select.query_selector_all("option")
                    val_to_select = ""
                    for opt in options:
                        if "Assisted Living Facilities" in opt.text_content():
                            val_to_select = opt.get_attribute("value")
                            break
                    
                    if val_to_select:
                        print(f"👉 Selecting 'Assisted Living Facilities' (Value={val_to_select})...")
                        target_select.select_option(value=val_to_select)
                    else:
                        print("❌ Could not find option value.")
                        return

                    # 2. Click Search (Submit)
                    print("👉 Clicking Search...")
                    # Usually "Search" button
                    page.click("input[type='submit'][value='Search'], button:has-text('Search')")
                    page.wait_for_load_state("networkidle")
                
                else:
                    print("❌ Facility Type dropdown NOT found. Checking for 'Next' or 'Agree' buttons...")
                    # Fallback logic here if needed
                    page.screenshot(path="alf_error_structure.png")
                    return

            except Exception as e:
                print(f"❌ Error during form interaction: {e}")
                page.screenshot(path="alf_error_interact.png")
                return

            # 3. Scrape Results
            print("📥 Scraping Results Table...")
            # Wait for table
            page.wait_for_selector("table", timeout=10000)
            
            # Simple Text Extraction for PoC (We can refine selectors)
            # Find the main data table. Usually the largest one.
            tables = page.query_selector_all("table")
            best_table = None
            max_rows = 0
            
            for t in tables:
                rows = t.query_selector_all("tr")
                if len(rows) > max_rows:
                    max_rows = len(rows)
                    best_table = t
            
            print(f"✅ Found Data Table with {max_rows} rows.")
            
            if not best_table:
                print("❌ No data table found.")
                return

            # Extract Data
            data = []
            rows = best_table.query_selector_all("tr")
            
            # Headers
            headers = [th.text_content().strip() for th in rows[0].query_selector_all("th")]
            if not headers:
                # Try first row as td
                headers = [td.text_content().strip() for td in rows[0].query_selector_all("td")]
            
            print(f"HEADERS: {headers}")
            
            for row in rows[1:]:
                cells = row.query_selector_all("td")
                if cells:
                    row_data = [cell.text_content().strip().replace("\n", " ") for cell in cells]
                    # Ensure alignment
                    if len(row_data) == len(headers):
                        data.append(row_data)
                    else:
                        # Handle mismatch or print
                        pass

            # create DF
            df = pd.DataFrame(data, columns=headers)
            print(f"📊 Extracted {len(df)} facilities.")
            
            # Save
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"💾 Saved to {OUTPUT_FILE}")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            page.screenshot(path="alf_critical_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_alf()
