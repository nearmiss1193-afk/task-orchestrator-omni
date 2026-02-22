"""
AUTONOMOUS SCRAPING TUNER
Runs daily to analyze the best performing niches ("replied" or "won" status).
Feeds the top niches into Grok/Gemini to generate 30 hyper-specific, highly-converting 
search queries, and saves them to `system_state.prospector_dynamic_niches`.
"""
import os
import json
import requests
import sys
from datetime import datetime, timezone

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if "/root" not in sys.path:
    sys.path.append("/root")

from modules.database.supabase_client import get_supabase

def run_tuning_cycle():
    print(f"\n{'='*60}")
    print(f"🧠 AUTONOMOUS SCRAPING TUNER — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")

    supabase = get_supabase()

    # 1. Analyze historical performance
    # Fetch all leads that have replied or converted
    print("📊 Analyzing conversion data from contacts_master...")
    try:
        # We look for positive engagement statuses
        res = supabase.table("contacts_master").select("niche, status").in_("status", ["replied", "won", "customer", "meeting_booked"]).execute()
        leads = res.data
    except Exception as e:
        print(f"❌ Failed to fetch contacts: {e}")
        return

    if not leads:
        print("⚠️ Not enough conversion data yet. Falling back to default baseline niches for generation.")
        top_niches = ["hvac contractor", "plumbing company", "roofing contractor"]
    else:
        # Score niches
        niche_counts = {}
        for lead in leads:
            n = lead.get("niche")
            if n:
                niche_counts[n] = niche_counts.get(n, 0) + 1
        
        # Sort by highest converting
        top_niches = sorted(niche_counts.items(), key=lambda x: x[1], reverse=True)
        top_niches = [n[0] for n in top_niches][:5]
        print(f"🏆 Top performing niches currently: {top_niches}")

    # 2. Generate New Optimized Niches via LLM
    print("🤖 Requesting optimal permutations from Intelligence Layer...")
    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key:
        print("❌ Missing GROK_API_KEY for tuning.")
        return

    prompt = f"""You are the Master Data Strategist for an AI automation agency.
Our prospector engine searches Google Places to find local businesses to pitch AI receptionists and missed-call-text-back systems to.

Based on our empirical data, these are our highest converting niches right now:
{json.dumps(top_niches)}

YOUR TASK:
Generate exactly 30 hyper-specific variations and entirely new but related niches that we should scrape next. 
Don't use generic terms like "plumber". Use terms like "24/7 emergency commercial plumber", "water damage restoration", "AC repair near me", etc.
The goal is to find businesses that have high call volumes, high ticket values, and a high cost of missing a call.

OUTPUT FORMAT:
Return ONLY a valid JSON array of strings. No markdown, no backticks, no explanations.
Example: ["24/7 HVAC repair", "emergency water damage restoration", "commercial roofing contractor"]
"""

    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "grok-3",
                "temperature": 0.8
            },
            timeout=45
        )
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content'].strip()
        
        # Clean possible markdown formatting
        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:-1]).strip()
            
        new_niches = json.loads(content)
        
        if not isinstance(new_niches, list) or len(new_niches) < 5:
            raise ValueError("Output was not a valid list of niches.")
            
        print(f"🎯 Generated {len(new_niches)} new optimized niches. Example: {new_niches[:3]}")
    except Exception as e:
        print(f"❌ Intelligence error: {e}")
        return

    # 3. Save to System State
    print("💾 Committing dynamic niches to system_state.prospector_dynamic_niches...")
    try:
        supabase.table("system_state").upsert({
            "key": "prospector_dynamic_niches",
            "status": "working",
            "last_error": json.dumps(new_niches),  # Stored as JSON string
            "updated_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="key").execute()
        # Also log to system_health
        import uuid
        supabase.table("system_health_log").insert({
            "id": str(uuid.uuid4()),
            "check_type": "tuning",
            "status": "tuning_complete",
            "details": json.dumps({
                "top_historical_niches": top_niches,
                "generated_count": len(new_niches)
            })
        }).execute()
        print("✅ Autonomous Tuning Cycle Complete.")
    except Exception as e:
        import traceback
        print(f"❌ Failed to save to database: {e}")
        try:
            print("API Error Details:", getattr(e, 'details', 'No details available'))
            print("API Error Hint:", getattr(e, 'hint', 'No hint'))
            print("API Error Message:", getattr(e, 'message', 'No message'))
        except:
            pass
        traceback.print_exc()

if __name__ == "__main__":
    if not os.environ.get("SUPABASE_URL"):
        from dotenv import load_dotenv
        load_dotenv()
    run_tuning_cycle()
