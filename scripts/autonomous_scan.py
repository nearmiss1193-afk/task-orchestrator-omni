
import json
import time
import os
from playwright.sync_api import sync_playwright
from lighthouse_api import get_pagespeed_data # Reuse existing API tool

OUTPUT_FILE = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_reports\facts.json"

class AutonomousScanner:
    def scan_site(self, url):
        facts = {
            "site_title": None,
            "footer_links": [],
            "contact_form": {
                "fields": [],
                "submit_button": None,
                "consent_checkbox": False,
                "privacy_link_near_form": False,
                "tcp_consent_text": None
            },
            "broken_links": [],
            "forms_loading": False,
            "buttons_working": True, # Assume true unless error found
            "page_speed": 0,
            "mobile_bounce": "approx 20%"
        }

        print(f"🕵️ RUNNING PROMPT 1: Scanning {url}...")

        # 1. PLAYWRIGHT SCAN
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
            
            try:
                response = page.goto(url, timeout=30000, wait_until="networkidle")
                if not response:
                    print("❌ Failed to load page")
                    return facts
                
                facts["site_title"] = page.title()
                
                # Footer Links
                footer_links = page.evaluate("""() => {
                    const links = Array.from(document.querySelectorAll('footer a, .footer a'));
                    return links.map(a => a.innerText.toLowerCase() + '|' + a.href);
                }""")
                
                normalized_links = []
                for l in footer_links:
                    txt, href = l.split('|', 1)
                    if 'privacy' in txt or 'privacy' in href: normalized_links.append('privacy-policy')
                    if 'terms' in txt or 'conditions' in txt: normalized_links.append('terms-conditions')
                    if 'sitemap' in txt: normalized_links.append('sitemap')
                facts["footer_links"] = list(set(normalized_links))

                # Contact Form (Check Home first, then /contact)
                forms = page.locator("form")
                contact_page_loaded = False
                
                if forms.count() == 0:
                    # Try /contact
                    try:
                        page.goto(url.rstrip('/') + "/contact", timeout=10000)
                        contact_page_loaded = True
                        forms = page.locator("form")
                    except:
                        pass
                
                if forms.count() > 0:
                    facts["forms_loading"] = True
                    form = forms.first
                    
                    # Fields
                    facts["contact_form"]["fields"] = form.locator("input, textarea").evaluate_all("els => els.map(e => e.name || e.placeholder || e.type)")
                    
                    # Submit Button
                    submit = form.locator("button[type='submit'], input[type='submit']")
                    if submit.count() > 0:
                        facts["contact_form"]["submit_button"] = submit.first.inner_text() or "Submit"
                    
                    # Consent Checkbox
                    checkboxes = form.locator("input[type='checkbox']")
                    facts["contact_form"]["consent_checkbox"] = checkboxes.count() > 0
                    
                    # TCPA Text & Privacy Link near form
                    form_text = form.inner_text().lower()
                    if "agree" in form_text or "consent" in form_text:
                        # Extract the sentence
                        facts["contact_form"]["tcp_consent_text"] = "Present (Generic)" # Simplified for now
                    
                    if "privacy" in form_text:
                        facts["contact_form"]["privacy_link_near_form"] = True

            except Exception as e:
                print(f"❌ Scan Error: {e}")

            finally:
                browser.close()

        # 2. PAGESPEED (Lighthouse API)
        print("⚡ Fetching PageSpeed...")
        ps_data = get_pagespeed_data(url, strategy="mobile")
        if "performance" in ps_data:
            facts["page_speed"] = ps_data["performance"]
            if facts["page_speed"] < 50:
                facts["mobile_bounce"] = "approx 40%"
            elif facts["page_speed"] < 90:
                facts["mobile_bounce"] = "approx 20%"
            else:
                facts["mobile_bounce"] = "< 10%"

        # Save Facts
        with open(OUTPUT_FILE, "w") as f:
            json.dump(facts, f, indent=2)
        
        print(f"✅ Facts saved to {OUTPUT_FILE}")
        print(json.dumps(facts, indent=2))
        return facts

if __name__ == "__main__":
    scanner = AutonomousScanner()
    scanner.scan_site("https://yourlakelanddentist.com")
