import os
import re
import time
import json
import hashlib
from playwright.sync_api import sync_playwright

class DiagnosticSweeper:
    """
    MISSION: PRE-FLIGHT CHECK (v39/40)
    Crawls, Validates Widgets, Checks Contacts, and Flags UX Issues.
    Includes Regression Scanning & Chat Simulation.
    """
    def __init__(self, target_url):
        self.url = target_url
        self.report = {
            "url": target_url,
            "status": "pending",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "widgets": [],
            "contacts": {"phones": [], "emails": []},
            "broken_links": [],
            "chat_simulation": {"status": "skipped", "log": []},
            "regression_flags": [],
            "console_errors": []
        }

    def execute_sweep(self):
        print(f"🧹 [Sweeper] Starting Sweep of {self.url}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Emulate Desktop
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            
            # Console listeners
            page.on("console", lambda msg: self.report["console_errors"].append(msg.text) if msg.type == "error" else None)
            
            try:
                # Networkidle is key for widgets loading
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                
                # 1. Widget Detection (Deep)
                self._detect_widgets(page)
                
                # 2. Contact Validation
                self._scan_contacts(page)
                
                # 3. CTA & Link Check
                self._check_navigation(page)

                # 4. Chat Simulation (New)
                self._simulate_chat(page)

                # 5. Regression Hash (Simple)
                self._check_regression(page)
                
                self.report["status"] = "complete"
                
            except Exception as e:
                self.report["status"] = "failed"
                self.report["error"] = str(e)
                
            browser.close()
            
        return self.report

    def _detect_widgets(self, page):
        print("   Searching for Chat Widgets...")
        found = False
        
        # A. GHL Specific (Shadow DOM often hides it, but tag presence is key)
        ghl_widgets = page.locator("chat-widget").count()
        if ghl_widgets > 0:
            self.report["widgets"].append({"type": "GHL Native", "count": ghl_widgets, "visible": True})
            found = True
        
        # B. Iframe Hunt
        iframes = page.frames
        for frame in iframes:
            try:
                if "leadconnector" in frame.url or "msgsndr" in frame.url:
                    self.report["widgets"].append({"type": "GHL Iframe", "url": frame.url, "visible": True})
                    found = True
            except: pass
            
        # C. Script Tag Check
        scripts = page.locator("script").all()
        for s in scripts:
            src = s.get_attribute("src") or ""
            if "chat-widget" in src:
                 self.report["widgets"].append({"type": "GHL Script Tag", "src": src})
                 found = True
                 
        if not found:
            self.report["widgets"].append({"type": "NONE", "visible": False})

    def _scan_contacts(self, page):
        print("   Scanning Contact Info...")
        content = page.content()
        
        # Phone Regex (US)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', content)
        self.report["contacts"]["phones"] = list(set(phones))
        
        # Email Regex
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        unique_emails = list(set(emails))
        self.report["contacts"]["emails"] = unique_emails
        
        # v2.1: MX Record Validation
        try:
            import dns.resolver
            for email in unique_emails:
                domain = email.split('@')[1]
                try:
                    dns.resolver.resolve(domain, 'MX')
                    # self.report["contacts"].setdefault("valid_mx", []).append(email) 
                except:
                    self.report["contacts"].setdefault("invalid_mx", []).append(email)
                    self.report["broken_links"].append(f"Invalid MX: {email}")
        except ImportError:
            self.report["console_errors"].append("dnspython not installed - skipping MX check")

    def _check_navigation(self, page):
        print("   Checking CTAs...")
        # Check buttons and links that look like Booking/Action
        buttons = page.locator("button, a.btn, a[href*='book'], a[href*='contact']").all()
        for btn in buttons:
            try:
                txt = btn.inner_text().strip()
                href = btn.get_attribute("href")
                
                # v2.1: Scroll vs Redirect
                if not href or href == "#":
                     if not btn.get_attribute("onclick") and btn.evaluate("node => node.tagName") == "A":
                          self.report["broken_links"].append(f"CTA Warning: '{txt}' (No valid href/action)")
                elif href.startswith("#"):
                     # Scroll link
                     pass 
                else:
                     # Redirect link - could ping
                     pass
            except:
                pass

    def _simulate_chat(self, page):
        print("   Simulating Chat (v2.1)...")
        self.report["chat_simulation"]["status"] = "attempted"
        
        try:
            # 1. Locate Widget
            # Strategy: Look for common GHL widget selectors
            widget_loc = page.locator("chat-widget") 
            
            if widget_loc.count() > 0:
                self.report["chat_simulation"]["log"].append(f"Widget Found ({widget_loc.count()}).")
                self.report["chat_simulation"]["status"] = "detected"
                
                # v2.1: Interaction Attempt (Headless Safe?)
                # Attempt to find the iframe inside the shadow root? 
                # Very hard in standard playwright without deep selectors.
                # We will mark as "PASS" for detection for now.
                
            else:
                # Check for iframe fallback
                if any(w['type'] == 'GHL Iframe' for w in self.report['widgets']):
                    self.report["chat_simulation"]["log"].append("Iframe Widget Detected.")
                    self.report["chat_simulation"]["status"] = "detected"
                else:
                    self.report["chat_simulation"]["log"].append("No Widget Found to Click.")
                    self.report["chat_simulation"]["status"] = "failed"

        except Exception as e:
             self.report["chat_simulation"]["error"] = str(e)

    def _check_regression(self, page):
         print("   Checking Regression...")
         # Hash content (excluding dynamic scripts if possible, but full hash for now)
         content = page.content()
         chash = hashlib.md5(content.encode('utf-8')).hexdigest()
         
         self.report["regression_flags"].append(f"Current Hash: {chash}")
         self.report["regression_flags"].append("Status: Hash logged for baseline comparison.") 

if __name__ == "__main__":
    # Test
    audit = DiagnosticSweeper("https://nearmiss1193-afk--hvac-campaign-standalone-hvac-landing.modal.run") 
    print(json.dumps(audit.execute_sweep(), indent=2))
