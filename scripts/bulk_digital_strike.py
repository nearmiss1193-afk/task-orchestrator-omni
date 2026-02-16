import os
import sys
import uuid
import json
from datetime import datetime

# Add root to path
sys.path.append(os.getcwd())

from modules.database.supabase_client import get_supabase
from workers.audit_generator import generate_audit_for_lead

def run_bulk_strike():
    print("🚀 Starting Bulk Digital Strike (Local Execution)...")
    supabase = get_supabase()
    
    # Leads we just inserted
    lead_names = [
        "Aesthetic & Implant Dentistry",
        "Mia Spa & Massage",
        "Keith Hargrove - State Farm",
        "Northside Asian Kitchen"
    ]
    
    for name in lead_names:
        try:
            print(f"\n🎯 Processing: {name}")
            res = supabase.table("contacts_master").select("*").ilike("company_name", f"%{name}%").execute()
            
            if not res.data:
                print(f"  ❌ Lead not found in DB")
                continue
                
            lead = res.data[0]
            lead_id = lead['id']
            print(f"  Lead found: {lead.get('email')} | {lead.get('website_url')}")
            
            # 1. Generate Audit
            audit = generate_audit_for_lead(lead)
            
            if not audit["success"]:
                print(f"  ❌ Audit generation failed: {audit.get('error')}")
                continue
                
            # 2. Store in audit_reports
            report_id = str(uuid.uuid4())[:12]
            ar = audit["audit_results"]
            
            supabase.table("audit_reports").insert({
                "report_id": report_id,
                "lead_id": lead_id,
                "company_name": lead.get("company_name"),
                "website_url": lead.get("website_url"),
                "audit_results": {
                    "pagespeed": ar["pagespeed"],
                    "privacy": ar["privacy"],
                    "ai_readiness": ar["ai_readiness"],
                    "criticals": ar["criticals"],
                },
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            report_url = f"https://www.aiserviceco.com/report.html?id={report_id}"
            print(f"  ✅ Report Generated: {report_url}")
            print(f"  📊 Stats: Score {ar['pagespeed'].get('score')}/100 | Privacy: {ar['privacy']['status']}")
            
        except Exception as e:
            print(f"  ❌ Processing error: {e}")

if __name__ == "__main__":
    run_bulk_strike()
