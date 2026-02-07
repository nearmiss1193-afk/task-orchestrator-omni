
from playwright.sync_api import sync_playwright

class LegalScraper:
    def __init__(self):
        pass

    def analyze_site(self, url):
        """
        Scrapes the site for:
        1. Footer Links (Privacy, Terms)
        2. Contact Form Consent
        """
        results = {
            "privacy_found": False,
            "terms_found": False,
            "contact_consent_found": False,
            "contact_form_found": False
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print(f"   🔍 Scraping {url} for legal markers...")
            try:
                page.goto(url, timeout=30000)
                
                # 1. TEXT / LINK SEARCH (Global)
                content = page.content().lower()
                links = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText.toLowerCase(), href: a.href.toLowerCase()}))
                }""")
                
                # Privacy
                for link in links:
                    if "privacy" in link['text'] or "privacy" in link['href']:
                        results["privacy_found"] = True
                        break
                
                # Terms
                for link in links:
                    if "terms" in link['text'] or "conditions" in link['text'] or "tos" in link['href']:
                        results["terms_found"] = True
                        break

                # 2. CONTACT FORM ANALYSIS
                # Navigate to contact page if possible, or check current page if it seems to be one
                contact_page_found = False
                if "/contact" in url or "contact" in url:
                    contact_page_found = True
                else:
                    # Try to find a contact link
                    contact_url = None
                    for link in links:
                        if "contact" in link['text'] or "contact" in link['href']:
                            contact_url = link['href']
                            break
                    
                    if contact_url:
                        print(f"   ➡️ Navigating to Contact Page: {contact_url}")
                        try:
                            page.goto(contact_url, timeout=15000)
                            contact_page_found = True
                        except:
                            print("   ⚠️ Could not load contact page.")

                # Check for form
                if page.locator("form").count() > 0:
                    results["contact_form_found"] = True
                    
                    # Check for "I agree" or checkbox near submit
                    # This is heuristical
                    page_text = page.inner_text("body").lower()
                    if "i agree" in page_text or "consent" in page_text:
                        # Check strictly for checkbox inputs
                        checkboxes = page.locator("input[type='checkbox']").count()
                        if checkboxes > 0:
                            results["contact_consent_found"] = True
            
            except Exception as e:
                print(f"   ❌ Scraper Error: {e}")
            
            finally:
                browser.close()

        return results

if __name__ == "__main__":
    scraper = LegalScraper()
    print(scraper.analyze_site("https://yourlakelanddentist.com"))
