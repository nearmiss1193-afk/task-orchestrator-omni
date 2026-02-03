"""
MISSION: SANDBOX WORKER - High-Velocity Experimentation
Routes a small subset of traffic (1%) to experimental hooks and APIs.
"""
import random
from modules.database.supabase_client import get_supabase
from utils.error_handling import brain_log

def is_sandbox_lead(lead_id: str) -> bool:
    """Deterministically (or randomly) assigns 1% of leads to the sandbox."""
    # Deterministic based on ID hash for consistency if needed, 
    # but for 1% R&D, simple random or modulo is fine.
    # Using modulo on lead_id if it's numeric/hex, or just random.randint.
    return random.random() < 0.01

def get_experimental_hook(supabase):
    """Fetches the latest experimental strategy from system_wisdom."""
    res = supabase.table("system_wisdom")\
        .select("topic, examples")\
        .eq("category", "horizon_rd")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    if res.data:
        opportunity = res.data[0].get('examples', {}).get('opportunity')
        return opportunity or res.data[0]['topic']
    return "Experimental SearchGPT Value Proposition"

def execute_sandbox_pulse(lead_id: str):
    """Executes a sandbox-specific outreach attempt."""
    supabase = get_supabase()
    
    hook = get_experimental_hook(supabase)
    print(f"🧪 SANDBOX EXECUTION: Lead {lead_id} | strategy: {hook}")
    
    # In a real scenario, this would call dispatch_email_logic with a custom template
    # or a dedicated Sandbox Dispatcher.
    
    brain_log(supabase, f"SANDBOX PAIRED: Lead {lead_id} using strategy '{hook[:50]}...'", "INFO")
    
    # Mark the lead as sandbox-tested in outbound_touches
    supabase.table("outbound_touches").insert({
        "phone": "SANDBOX",
        "channel": "experiment",
        "company": f"SANDBOX: {hook[:30]}",
        "status": "initiated",
        "meta": {"lead_id": lead_id, "is_sandbox": True}
    }).execute()

if __name__ == "__main__":
    # Test logic
    execute_sandbox_pulse("test-lead-123")
