"""
MISSION: SELF-LEARNING LOOP (Phase 5)
Analyzing outreach outcomes to refine strategies 
and update Sales Sarah's prompt dynamically.
"""

import os
import sys
import modal
from datetime import datetime, timezone, timedelta

# Ensure root is in path
if "/root" not in sys.path:
    sys.path.append("/root")

from core.image_config import image, VAULT
from core.apps import engine_app as app

def trigger_self_learning_loop():
    """
    1. Load outreach logs from Supabase
    2. Run EmpireBrain.reflect_and_optimize()
    3. Update system insights
    4. Log the evolution
    """
    from modules.database.supabase_client import get_supabase
    from modules.learning.brain import EmpireBrain
    
    print(f"🧠 BRAIN REFLECTION START: {datetime.now(timezone.utc).isoformat()}")
    
    try:
        brain = EmpireBrain()
        insights = brain.reflect_and_optimize()
        
        # Log the learning event
        supabase = get_supabase()
        supabase.table("sovereign_logs").insert({
            "log_level": "info",
            "message": "Brain reflected and optimized strategy.",
            "details": {"insights": insights},
            "source": "self_learning_cron"
        }).execute()
        
        print(f"✅ Strategy updated. Focus Niche: {insights.get('focus_niche', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Brain Reflection Error: {e}")

if __name__ == "__main__":
    pass
