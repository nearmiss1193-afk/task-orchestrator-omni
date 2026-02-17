"""
MISSION: MANUS HIRING STRIKE (Sprint Upgrade)
Triggers the Maya v2 "Recruitment Screener" persona for existing Manus leads.
Targets the 19 hiring-based leads sitting in the pipeline.
"""
import sys
import os

if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.apps import engine_app as app
from core.image_config import image, VAULT

@app.function(image=image, secrets=[VAULT])
def execute_manus_strike():
    from modules.database.supabase_client import get_supabase
    from workers.outreach import dispatch_email_logic
    import time
    
    supabase = get_supabase()
    
    # 1. Fetch leads from Manus source that haven't had outreach yet
    print("🎯 Fetching Manus recruitment leads for the strike...")
    res = supabase.table("contacts_master") \
        .select("*") \
        .eq("source", "manus") \
        .in_("status", ["new", "research_done"]) \
        .execute()
    
    leads = res.data or []
    print(f"🔥 Found {len(leads)} leads for the strike.")
    
    if not leads:
        print("😴 No Manus leads ready for strike. Mission complete.")
        return
    
    # 2. Trigger outreach for each lead
    success_count = 0
    for lead in leads:
        try:
            print(f"🚀 Launching strike for {lead.get('company_name')} ({lead.get('email')})...")
            # dispatch_email_logic has the 'hiring_trigger' template built-in
            # We just need to ensure the source/status triggers the right path
            res = dispatch_email_logic.local(lead['id'])
            if res:
                success_count += 1
                print(f"✅ Strike Successful: {lead.get('company_name')}")
            else:
                print(f"⚠️ Strike Failed for {lead.get('company_name')}")
                
            # Rate limiting for deliverability safe-guard
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error striking lead {lead['id']}: {e}")
            
    print(f"🏁 Strike Complete: {success_count}/{len(leads)} leads engaged.")

if __name__ == "__main__":
    # Local trigger bridge
    with app.run():
        execute_manus_strike.local()
