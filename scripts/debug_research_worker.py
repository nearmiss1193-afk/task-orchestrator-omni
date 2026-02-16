import os, json, uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from modules.database.supabase_client import get_supabase
from workers.audit_generator import fetch_pagespeed, check_privacy_policy, check_ai_readiness

load_dotenv()

def debug_worker(lead_id):
    print(f"🕵️ DEBUG: Auditing Lead {lead_id}...")
    supabase = get_supabase()
    
    try:
        lead = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute().data
        if not lead or not lead.get("website_url"):
            print(f"  ⚠️ Research failed: Lead {lead_id} not found or no website")
            return
            
        url = lead["website_url"]
        
        # 1. Run PageSpeed
        print(f"  [1/3] PageSpeed Insights for {url}...")
        ps_data = fetch_pagespeed(url)
        print(f"  Result: {ps_data}")
        
        # 2. Check FDBR (Privacy)
        print(f"  [2/3] Privacy/FDBR Check...")
        privacy_data = check_privacy_policy(url)
        print(f"  Result: {privacy_data}")
        
        # 3. Check AI Readiness
        print(f"  [3/3] AI Readiness Check...")
        ai_data = check_ai_readiness(url)
        print(f"  Result: {ai_data}")
        
        # 4. Integrate into raw_research
        raw_research = json.loads(lead.get("raw_research") or "{}")
        raw_research.update({
            "pagespeed": ps_data,
            "privacy": privacy_data,
            "ai_readiness": ai_data,
            "audited_at": datetime.now(timezone.utc).isoformat()
        })
        
        print(f"✅ RESEARCH PREVIEW: {lead.get('company_name')} (Score: {ps_data.get('score', 'N/A')}/100)")
        
    except Exception as e:
        import traceback
        print(f"❌ RESEARCH ERROR [Lead {lead_id}]: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Use one of the eligible leads from earlier
    test_id = "474f4269-17ae-4d09-b95f-9568778f7af0"
    debug_worker(test_id)
