"""
SYSTEM VERIFICATION SCRIPT
===========================
Checks all critical components and reports status.
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# === SUPABASE CHECK ===
print("\n" + "="*60)
print("📊 SYSTEM VERIFICATION REPORT")
print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

try:
    from supabase import create_client
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("\n❌ SUPABASE: Missing credentials")
    else:
        supabase = create_client(url, key)
        
        # Total leads
        leads = supabase.table("leads").select("*").execute()
        total_leads = len(leads.data) if leads.data else 0
        
        # Leads with audit links (ready for contact)
        ready_leads = [l for l in (leads.data or []) if l.get("audit_link")]
        
        # Leads contacted today
        today = datetime.now().date().isoformat()
        contacted_today = [l for l in (leads.data or []) if l.get("contacted_at", "").startswith(today)]
        
        # Leads with emails sent
        emailed = [l for l in (leads.data or []) if l.get("email_sent")]
        
        print(f"\n📈 LEAD PIPELINE:")
        print(f"   Total Prospects: {total_leads}")
        print(f"   Ready (with audit link): {len(ready_leads)}")
        print(f"   Emailed: {len(emailed)}")
        print(f"   Contacted Today: {len(contacted_today)}")
        
        # Show last 10 leads
        print(f"\n📋 LAST 10 PROSPECTS:")
        for lead in (leads.data or [])[-10:]:
            name = lead.get("company_name", "Unknown")
            email = lead.get("email", "N/A")
            has_audit = "✅" if lead.get("audit_link") else "❌"
            was_emailed = "📧" if lead.get("email_sent") else "⏳"
            print(f"   {has_audit} {was_emailed} {name[:40]} | {email}")
            
except Exception as e:
    print(f"\n❌ SUPABASE ERROR: {e}")

# === BRAIN LOG CHECK ===
print("\n" + "-"*60)
print("🧠 BRAIN LOG STATUS:")
try:
    brain_log_path = "brain_log.json"
    if os.path.exists(brain_log_path):
        with open(brain_log_path, 'r') as f:
            brain_log = json.load(f)
        print(f"   Entries: {len(brain_log)}")
        if brain_log:
            last_entry = brain_log[-1]
            print(f"   Last Entry: {last_entry.get('type')} - {last_entry.get('timestamp', 'N/A')}")
    else:
        print("   No brain_log.json found (awaiting first success)")
except Exception as e:
    print(f"   Error reading brain log: {e}")

# === STRATEGY CONFIG CHECK ===
print("\n" + "-"*60)
print("🎯 STRATEGY CONFIG:")
try:
    strategy_path = "strategy_config.json"
    if os.path.exists(strategy_path):
        with open(strategy_path, 'r') as f:
            strategy = json.load(f)
        print(f"   Target Niche: {strategy.get('target_niche', 'N/A')}")
        print(f"   Last Updated: {strategy.get('updated_at', 'N/A')}")
    else:
        print("   No strategy_config.json (using defaults)")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
