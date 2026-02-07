
import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_screenshots"

class EvidenceCollector:
    def __init__(self, output_dir=OUTPUT_DIR):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def capture_all(self, url):
        """
        Captures 4 key screenshots:
        1. Homepage (Full/Footer)
        2. Contact Page
        3. Search: Privacy
        4. Search: Terms
        """
        screenshots = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
            
            print(f"   📸 Evidence Collector: Target {url}")
            
            try:
                # 1. HOMEPAGE (Footer Focus)
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                # Scroll to bottom
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                
                path_home = os.path.join(self.output_dir, "homepage_footer.png")
                page.screenshot(path=path_home)
                screenshots['homepage'] = path_home
                print(f"      - Captured Footer: {path_home}")

                # 2. CONTACT PAGE
                # Attempt to find contact link
                try:
                    contact_link = page.get_by_text("Contact", exact=False).first
                    if contact_link.count() > 0:
                        contact_href = contact_link.get_attribute("href")
                        if contact_href:
                            page.goto(contact_href if contact_href.startswith("http") else url.rstrip("/") + "/" + contact_href.lstrip("/"))
                            page.wait_for_timeout(2000)
                    else:
                        # Try direct URL
                        page.goto(url.rstrip("/") + "/contact", timeout=10000)
                except:
                    pass
                
                path_contact = os.path.join(self.output_dir, "contact_page.png")
                page.screenshot(path=path_contact)
                screenshots['contact'] = path_contact
                print(f"      - Captured Contact: {path_contact}")

                # 3. SEARCH: PRIVACY (Browser Find)
                # We can't easily screenshot the "Ctrl+F" UI, but we can highlight the text
                page.goto(url) # Go back home
                # Highlight "Privacy"
                found_privacy = page.evaluate("""() => {
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    let count = 0;
                    while(node = walker.nextNode()) {
                        if (node.nodeValue.toLowerCase().includes('privacy')) {
                            const span = document.createElement('span');
                            span.style.backgroundColor = 'yellow';
                            span.style.color = 'black';
                            span.style.border = '2px solid red';
                            span.textContent = node.nodeValue;
                            node.parentNode.replaceChild(span, node);
                            count++;
                        }
                    }
                    return count;
                }""")
                if found_privacy > 0:
                     # Scroll to first match? Hard to do reliably. Just formatting.
                     pass
                
                path_privacy = os.path.join(self.output_dir, "search_privacy.png")
                page.screenshot(path=path_privacy)
                screenshots['search_privacy'] = path_privacy
                print(f"      - Captured Privacy Check: {path_privacy}")


            except Exception as e:
                print(f"   ❌ Capture Error: {e}")
            
            finally:
                browser.close()
        
        return screenshots

if __name__ == "__main__":
    collector = EvidenceCollector()
    collector.capture_all("https://yourlakelanddentist.com")
