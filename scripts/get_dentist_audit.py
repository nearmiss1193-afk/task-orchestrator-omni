import os
from modules.database.supabase_client import get_supabase

def get_dentist_findings():
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase client initialization failed.")
        return

    # Target: Aesthetic & Implant Dentistry
    target_name = "Aesthetic & Implant Dentistry"
    
    print(f"🔍 Searching for audit: {target_name}")
    res = supabase.table("audit_reports").select("*").ilike("company_name", f"%{target_name}%").execute()
    
    if not res.data:
        print("  ❌ No audit report found for this company.")
        return
        
    audit = res.data[0]
    results = audit.get("audit_results", {})
    
    print("\n--- SPECIFIC FINDINGS ---")
    print(f"Report ID: {audit['report_id']}")
    print(f"PageSpeed Score: {results.get('pagespeed', {}).get('score', 'N/A')}")
    print(f"Privacy Status: {results.get('privacy', {}).get('status', 'N/A')}")
    print(f"AI Readiness: {results.get('ai_readiness', {}).get('status', 'N/A')}")
    print(f"Critical Findings: {results.get('criticals', 0)}")
    print(f"PDF URL: {audit.get('pdf_url')}")
    print(f"Report URL: https://www.aiserviceco.com/report.html?id={audit['report_id']}")

if __name__ == "__main__":
    get_dentist_findings()
