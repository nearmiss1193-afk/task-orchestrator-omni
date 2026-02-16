from modules.database.supabase_client import get_supabase
from workers.manus_dossier import generate_candidate_dossier
from workers.audit_generator import generate_audit_for_lead
import json

def run_phase12_strike():
    """
    Triggers the recruitment-bait strike for Phase 12.
    1. Generates Manus Dossiers.
    2. Generates Veo 3 Video Teasers (integrated in audit).
    """
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase connection failed")
        return
        
    print("🚀 ACTIVATING CINEMATIC STRIKE (PHASE 12)...")
    
    # Target leads with source='manus'
    res = supabase.table("contacts_master").select("*").eq("source", "manus").execute()
    leads = res.data
    
    if not leads:
        print("📭 No manus leads found in database.")
        return
        
    print(f"🎯 Striking {len(leads)} target businesses...")
    
    for lead in leads:
        company = lead.get('company_name')
        print(f"\n--- Strike Triggered: {company} ---")
        
        # 1. Candidate Dossier (Manus Pain)
        try:
            print(f"  📄 Generating Dossier for {company}...")
            dossier = generate_candidate_dossier(lead['id'])
            if dossier:
                print(f"  ✅ Dossier Persistent: {len(dossier)} characters")
        except Exception as e:
            print(f"  ❌ Dossier Failure for {company}: {e}")
            
        # 2. Cinematic Video + Audit (Pattern Interrupt)
        try:
            if lead.get('website_url'):
                print(f"  🎥 Generating Veo 3 Video for {company}...")
                audit = generate_audit_for_lead(lead)
                if audit.get('success'):
                    # The video URL is now in the audit results
                    video = audit['audit_results'].get('video_teaser_url')
                    print(f"  ✅ Cinematic Teaser Active: {video}")
            else:
                print(f"  ⚠️ Skipping Video: No website for {company}")
        except Exception as e:
            print(f"  ❌ Video/Audit Failure for {company}: {e}")

if __name__ == "__main__":
    run_phase12_strike()
