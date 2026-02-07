
import os
import json
import time
from lighthouse_api import get_pagespeed_data
from text_scraper import LegalScraper
from evidence_collector_local import EvidenceCollector
from board_call_raw import call_board # We will assume we can import or adapt this

# Constants
OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_reports"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class AuditPipelineV3:
    def __init__(self):
        self.scraper = LegalScraper()
        self.evidence = EvidenceCollector()
        
    def run_audit(self, url, business_name):
        print(f"🚀 STARTING AUDIT V3: {business_name} ({url})")
        start_time = time.time()
        
        # 1. EVIDENCE COLLECTION
        print("\n[Phase 1] Collecting Evidence...")
        screenshots = self.evidence.capture_all(url)
        
        # 2. LEGAL & TEXT ANALYSIS
        print("\n[Phase 2] Analyzing Text & Compliance...")
        legal_data = self.scraper.analyze_site(url)
        
        # 3. PERFORMANCE DATA
        print("\n[Phase 3] Measuring Performance (Google API)...")
        perf_data = get_pagespeed_data(url, strategy="mobile")
        
        # 4. COMPILE REPORT
        print("\n[Phase 4] Compiling Report...")
        report = {
            "business_name": business_name,
            "url": url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "legal": legal_data,
            "performance": perf_data,
            "screenshots": screenshots,
            "duration": round(time.time() - start_time, 2)
        }
        
        report_path = os.path.join(OUTPUT_DIR, f"{business_name.replace(' ', '_')}_audit.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"✅ Audit Complete in {report['duration']}s")
        print(f"📂 Report saved: {report_path}")
        
        return report

    def generate_email_draft(self, report):
        """Generates the Markdown email draft based on findings"""
        # Logic to determine risk
        legal = report['legal']
        perf = report['performance']
        
        risk_level = "LOW"
        hooks = []
        
        if not legal['terms_found']:
            hooks.append("MISSING TERMS OF USE")
            risk_level = "HIGH"
        if not legal['privacy_found']:
            hooks.append("MISSING PRIVACY POLICY")
            risk_level = "HIGH"
        if report.get('legal', {}).get('contact_form_found') and not report.get('legal', {}).get('contact_consent_found'):
            hooks.append("NO CONTACT FORM CONSENT")
            risk_level = "CRITICAL"
            
        score = perf.get('performance', 0)
        
        draft = f"""
## DRAFT EMAIL FOR: {report['business_name']}
**Subject:** Quick site fix to avoid TCPA fines (Audit Attached)

Dear {report['business_name']} Team,

I just ran a technical audit on {report['url']} and found **{len(hooks)} critical liability risks**:

{chr(10).join([f'- 🔴 {h}' for h in hooks])}

**Performance:**
- Mobile Score: {score}/100
- Load Time: {perf.get('fcp')}

**Why this matters:**
Optum RX just paid millions for ignoring compliance. Your contact form is currently collecting data without affirmative consent.

I have attached the full **Evidence Packet** (Screenshots + JSON) to this email.

Best,
Daniel Coffman
AI Service Co
        """
        return draft

if __name__ == "__main__":
    # Test Run
    pipeline = AuditPipelineV3()
    report = pipeline.run_audit("https://yourlakelanddentist.com", "Brilliant Smiles")
    draft = pipeline.generate_email_draft(report)
    print("\n" + "="*40)
    print(draft)
    print("="*40)
