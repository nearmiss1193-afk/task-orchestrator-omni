"""
NEXUS ENGINE - WISDOM SYNTHESIS
Analyzes past outreach and call outcomes to generate persistent system wisdom.
"""
import sys
import os
if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT])
async def synthesize_wisdom():
    """
    Periodically runs to convert raw interactions into persistent wisdom.
    """
    from modules.database.supabase_client import get_supabase
    from modules.ai.routing import get_gemini_model
    import json
    
    sb = get_supabase()
    
    # 1. Fetch successful interactions (replies or bookings)
    # We look for contacts with 'replied' status or successful conversation outcomes
    success_contacts = sb.table("contacts_master").select("*").eq("status", "replied").limit(20).execute()
    
    if not success_contacts.data:
        print("ℹ️ No new successful interactions to analyze.")
        return
    
    # 2. Extract hook/strategy used for these successes
    context_data = []
    for contact in success_contacts.data:
        context_data.append({
            "company": contact.get("company_name"),
            "hook": contact.get("ai_strategy"),
            "vertical": contact.get("industry") or "service"
        })
        
    # 3. Use Gemini to find the pattern
    print(f"🧠 ANALYZING SUCCESS PATTERNS for {len(context_data)} contacts...")
    model = get_gemini_model("pro")
    prompt = f"Analyze these successful outreach hooks and extract 1 high-level 'Wisdom Insight' for the industry. Focus on WHY it worked. Hooks: {json.dumps(context_data)}"
    
    try:
        res = model.generate_content(prompt)
        insight = res.text.strip()
        print(f"✅ SYNTHESIZED WISDOM: {insight[:100]}...")
        
        # 4. Save to system_wisdom (Assume table exists or use fallback)
        try:
            sb.table("system_wisdom").insert({
                "category": "outreach_hook",
                "vertical": "general",
                "topic": "Success Pattern Analysis",
                "insight": insight,
                "confidence": 0.8,
                "examples": context_data
            }).execute()
            print("💾 WISDOM SAVED TO DATABASE.")
        except Exception as e:
            print(f"⚠️ Could not save to DB (table might not exist): {e}")
            # Fallback: Save to local or log
            
    except Exception as e:
        print(f"❌ WISDOM SYNTHESIS ERROR: {e}")

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("0 0 * * *")) # Every day at midnight
async def daily_wisdom_cron():
    await synthesize_wisdom.remote()
