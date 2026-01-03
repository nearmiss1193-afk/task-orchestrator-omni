
import json
import time

class CampaignVerifier:
    """
    MISSION: OMNI-VERIFICATION
    Aggregates all testing agents into a single report.
    """
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        
    def verify_all(self, target_url: str):
        print(f"🛡️ Starting Full Verification for: {target_url}")
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": target_url,
            "checks": []
        }
        
        # 1. VISUAL AUDIT (Site Auditor)
        from modules.sales.site_auditor import SiteAuditor
        auditor = SiteAuditor()
        audit_res = auditor.audit_site(target_url)
        
        check_visual = {
            "name": "Visual/Tech Audit",
            "status": "PASS" if audit_res.get('load_time', 10) < 3.0 else "WARN",
            "details": f"Load Time: {audit_res.get('load_time')}s | Widgets: {audit_res.get('widgets')}"
        }
        results["checks"].append(check_visual)
        
        # 2. FUNCTIONAL AUDIT (Secret Shopper)
        from modules.testing.secret_shopper import SecretShopper
        shopper = SecretShopper(self.supabase)
        try:
            shop_res = shopper.execute_shop()
            check_functional = {
                "name": "Lead Flow & Response",
                "status": "PASS" if shop_res.get('status') == 'success' else "FAIL",
                "details": f"Reply: {shop_res.get('reply', 'N/A')[:50]}..."
            }
        except Exception as e:
            check_functional = {
                "name": "Lead Flow & Response",
                "status": "FAIL",
                "details": str(e)
            }
        results["checks"].append(check_functional)
        
        # 3. SCHEMA HEALTH (Brain Logs Check)
        try:
            # Simple check if we can read logs
            self.supabase.table("brain_logs").select("id").limit(1).execute()
            check_db = {"name": "Database Connectivity", "status": "PASS", "details": "Read Verified"}
        except Exception as e:
            check_db = {"name": "Database Connectivity", "status": "FAIL", "details": str(e)}
        results["checks"].append(check_db)
        
        return results

    def generate_markdown(self, results):
        md = f"# 🛡️ Campaign Verification Report\n"
        md += f"**Date:** {results['timestamp']}\n"
        md += f"**Target:** {results['target']}\n\n"
        
        md += "| Check | Status | Details |\n"
        md += "| :--- | :--- | :--- |\n"
        
        for check in results["checks"]:
            icon = "✅" if check["status"] == "PASS" else "⚠️" if check["status"] == "WARN" else "❌"
            md += f"| {check['name']} | {icon} {check['status']} | {check['details']} |\n"
            
        return md
