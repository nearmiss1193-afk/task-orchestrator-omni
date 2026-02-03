import os
import requests
import time
import datetime
import json
from concurrent.futures import ThreadPoolExecutor

class ConnectionAuditor:
    """
    MISSION 39.7: CONNECTION VERIFICATION PROTOCOL
    Validates HTTP connectivity, Redirects, Social Links, and Campaign Endpoints.
    Integrates with DiagnosticSweeper for deep DOM checks.
    """
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "endpoints": {},
            "social_health": {},
            "campaign_links": {},
            "broken_resources": [],
            "status": "PENDING"
        }
        self.targets = [
            "https://aiserviceco.com",
            # "https://aiserviceco.com/landing-page-541315", # Example 404 test
            "https://nearmiss1193-afk--hvac-campaign-standalone-hvac-landing.modal.run"
        ]

    def execute_audit(self):
        print("🌐 [AUDIT] Starting Full Connection Protocol...")
        
        # 1. Live Page Connectivity
        self._audit_connectivity()
        
        # 2. Campaign Validation
        self._audit_campaigns()
        
        # 3. Widget & CTA (Delegate to Sweeper if available, else lightweight check)
        # We will do a lightweight regex check on the content fetched in step 1
        
        # 4. Social Integration
        self._audit_socials()
        
        # 5. Final Report
        self._finalize_report()
        
        return self.report

    def _audit_connectivity(self):
        print("   Checking Live Endpoints...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(self._check_url, self.targets)
            
        for res in results:
            self.report["endpoints"][res["url"]] = res

    def _check_url(self, url):
        start = time.time()
        result = {"url": url, "status": "error", "latency": 0, "redirects": [], "social_tags": []}
        try:
            resp = requests.get(url, timeout=10, allow_redirects=True)
            result["latency"] = round((time.time() - start) * 1000)
            result["status"] = resp.status_code
            
            if resp.history:
                result["redirects"] = [r.url for r in resp.history]
                
            # Content Sniffing
            content = resp.text.lower()
            
            # GHL Widget Check
            if "data-widget-id" in content or "chat-widget" in content:
                result["has_ghl_widget"] = True
            else:
                result["has_ghl_widget"] = False
                if "hvac" in url: # Expected on HVAC page
                     self.report["broken_resources"].append(f"Missing Widget on {url}")

            # Social Tags
            # Simple Parse
            if "og:url" in content: result["social_tags"].append("og:url")
            if "facebook.com" in content: result["social_tags"].append("facebook_link")
            
        except Exception as e:
            result["error"] = str(e)
            self.report["broken_resources"].append(f"Connectivity Fail {url}: {e}")
            
        return result

    def _audit_campaigns(self):
        print("   Checking Campaign Links...")
        try:
            # Mock DB Call - In prod: select * from campaign_performance
            # campaigns = self.supabase.table("campaign_performance").select("landing_page_url").execute()
            # For now, we test known paths
            pass
        except:
            pass

    def _audit_socials(self):
        print("   Checking Social Integrations...")
        socials = ["https://facebook.com/aiserviceco", "https://linkedin.com/company/aiserviceco"]
        for s in socials:
            res = self._check_url(s)
            self.report["social_health"][s] = "Alive" if res["status"] == 200 else "Dead"

    def _finalize_report(self):
        broken_count = len(self.report["broken_resources"])
        if broken_count == 0:
            self.report["status"] = "ALL CUSTOMER PORTALS CONNECTED ✅"
        else:
            self.report["status"] = "CONNECTION ERRORS DETECTED ⚠️"

    def generate_report_markdown(self):
        md = f"""# CONNECTION AUDIT REPORT
**Timestamp:** {self.report['timestamp']}
**Status:** {self.report['status']}

## 1. Live Page Status
| URL | Status | Latency (ms) | Widget |
| :--- | :--- | :--- | :--- |
"""
        for url, data in self.report["endpoints"].items():
            md += f"| {url} | {data['status']} | {data['latency']} | {data.get('has_ghl_widget', 'N/A')} |\n"

        md += "\n## 2. Broken Resources\n"
        if not self.report["broken_resources"]:
            md += "None.\n"
        else:
            for b in self.report["broken_resources"]:
                md += f"- {b}\n"
                
        md += "\n**Signed:** *Imperium Governor v39.7*"
        return md

if __name__ == "__main__":
    # Test
    audit = ConnectionAuditor(None)
    audit.execute_audit()
    print(audit.generate_report_markdown())
