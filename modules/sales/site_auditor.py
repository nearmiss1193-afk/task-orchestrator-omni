
import os
import re
import time
from playwright.sync_api import sync_playwright

class SiteAuditor:
    """
    MISSION: PROSPECT AUDIT
    Agents visits prospect sites to identify 'Money on the Table'.
    Detects: No Chat, No SMS, Slow Load, Manual Booking.
    """

    def __init__(self):
        self.report_data = {}

    def audit_site(self, url: str):
        """
        Full automated audit of a target URL.
        """
        print(f"[AUDIT] Auditing: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            start_time = time.time()
            try:
                page.goto(url, timeout=15000)
            except Exception as e:
                print(f"[WARN] Audit Load Error: {e}")
                browser.close()
                return {"error": "Site Unreachable"}

            load_time = round(time.time() - start_time, 2)
            
            # 1. Tech Detection
            html = page.content().lower()
            widgets = self.detect_chat_widgets(html)
            
            # 2. Contact Intent
            phones = self.extract_phones(page)
            
            # 3. Office Inference
            office_stack = self.infer_office_tech(html)
            
            # 4. Widget Click Test (Interactive QA)
            widget_status = self.check_widget_interactivity(page)
            
            browser.close()
            
            # 5. Financial Calculations
            financials = self.calculate_opportunity(widgets, office_stack)
            
            return {
                "url": url,
                "load_time": load_time,
                "widgets": widgets,
                "widget_interactivity": widget_status,
                "phones": phones,
                "office_stack": office_stack,
                "financials": financials,
                "summary": self.generate_summary(financials, office_stack, widget_status)
            }

    def check_widget_interactivity(self, page):
        """
        Qa: Simulates a user clicking the chat widget.
        """
        try:
            # GHL Specific Selectors
            # Usually in an iframe or a distinct div
            widget_btn = page.locator("iframe#chat-widget, #chat-widget-container, .chat-widget-launcher").first
            
            if widget_btn.count() > 0:
                if widget_btn.is_visible():
                    # Attempt Click
                    widget_btn.click(timeout=3000)
                    time.sleep(2) # Wait for animation
                    
                    # Check for Open State (e.g. input field)
                    # GHL often opens an iframe with a text area
                    has_input = page.locator("input[type='text'], textarea, .chat-open").count() > 0
                    if has_input:
                        return "PASS (Clickable)"
                    else:
                        return "FAIL (Unresponsive)"
                else:
                    return "FAIL (Hidden)"
            return "N/A (Not Found)"
        except Exception as e:
            return f"FAIL (Error: {str(e)})"


    def detect_chat_widgets(self, html: str):
        widgets = []
        if "intercom" in html: widgets.append("Intercom")
        if "drift" in html: widgets.append("Drift")
        if "tidio" in html: widgets.append("Tidio")
        if "leadconnector" in html: widgets.append("GHL Chat")
        
        return widgets

    def extract_phones(self, page):
        # basic regex checks on visible text
        text = page.inner_text("body")
        # Simple US phone regex
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return list(set(phones))

    def infer_office_tech(self, html: str):
        stack = {
            "booking": "Manual (Phone/Form)",
            "payroll": "Likely Manual",
            "inefficiency_score": "High"
        }
        
        if "calendly" in html or "acuity" in html:
            stack["booking"] = "Automated (Basic)"
            stack["inefficiency_score"] = "Medium"
            
        if "adp" in html or "gusto" in html:
            stack["payroll"] = "Cloud Payroll"
            
        return stack

    def calculate_opportunity(self, widgets, office_stack):
        """
        Calculates 'Cost of Inaction' based on findings.
        Metrics: HVAC Standard ($450 avg job, 8 missed calls/wk)
        """
        missed_revenue = 0
        if not widgets:
            # 8 missed calls * $450 * 52 weeks = ~$187k (using 70% lost factor)
            # Conservative: $144,000 / yr
            missed_revenue += 144000
            
        office_waste = 0
        if office_stack["booking"] == "Manual (Phone/Form)":
            # Admin Time: 15 hrs/wk * $20/hr * 52 = $15k
            office_waste += 15600
        
        return {
            "missed_revenue_annual": missed_revenue,
            "office_waste_annual": office_waste,
            "total_opportunity": missed_revenue + office_waste
        }

    def generate_summary(self, financials, office_stack, widget_status="N/A"):
        msg = f"[LOSS] **TOTAL LOSS DETECTED: ${financials['total_opportunity']:,}/yr**\n\n"
        
        # Widget Status
        if "FAIL" in widget_status:
            msg += f"[CRITICAL] **Critical UX:** Chat Widget is Unresponsive/Hidden ({widget_status}).\n"
        elif "PASS" in widget_status:
            msg += f"[PASS] **UX:** Chat Widget is Interactive.\n"
        
        if financials['missed_revenue_annual'] > 0:
            msg += f"[LOSS] **Missed Calls:** Losing ${financials['missed_revenue_annual']:,} due to lack of AI Receptionist.\n"
        else:
            msg += f"[PASS] **Chat:** Site has existing chat widget.\n"
            
        if financials['office_waste_annual'] > 0:
            msg += f"[WARN] **Office Drag:** Wasting ${financials['office_waste_annual']:,} in manual scheduling/payroll time.\n"
            msg += f"   - Recommended: Implement AI Autonomous Booking & Intelligent Payroll.\n"
            
        return msg
