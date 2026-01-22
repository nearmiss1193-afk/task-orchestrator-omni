import modal
import os
import sys
import json
import asyncio
import random
from typing import List, Dict, Optional

# Define the image
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "playwright", "google-generativeai", "duckduckgo-search")
    .run_commands("playwright install chromium")
)

# Mock data for fallback
MOCK_LEADS = {
    "emergency plumber": [
        {"name": "Rapid Response Plumbing", "phone": "+15550100", "website": "rapidplumb.com", "rating": 4.8, "reviews": 120},
        {"name": "24/7 Leak Fixers", "phone": "+15550101", "website": "leakfixers247.com", "rating": 3.5, "reviews": 15},
        {"name": "Old School Plumbers", "phone": "+15550102", "website": "", "rating": 5.0, "reviews": 200}, # No website = low neural score?
    ]
}

async def run_neural_hunt(niche: str, cities: List[str]):
    """
    Neural Prospecting Mission Logic
    """
    print(f"🧠 [NEURAL] Starting hunt for '{niche}' in {cities}")
    
    # Imports inside function (Modal pattern)
    import google.generativeai as genai
    from supabase import create_client
    try:
        from duckduckgo_search import DDGS
        HAS_SEARCH = True
    except ImportError:
        HAS_SEARCH = False
        print("⚠️ [NEURAL] duckduckgo-search not found, using mocks.")

    # Setup Clients
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not supabase_url or not supabase_key:
        print("❌ [NEURAL] Supabase credentials missing.")
        return {"error": "Missing Supabase creds"}

    supabase = create_client(supabase_url, supabase_key)
    
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            model = None
            print(f"⚠️ [NEURAL] Gemini config failed: {e}")
    else:
        model = None
        print("⚠️ [NEURAL] Gemini key missing. Using heuristic scoring.")

    total_leads = 0
    
    for city in cities:
        print(f"🕵️ [NEURAL] Scanning {city}...")
        raw_leads = []

        # 1. SEARCH PHASE
        if HAS_SEARCH:
            try:
                # Real search logic
                with DDGS() as ddgs:
                    query = f"{niche} in {city}"
                    # Try-catch specifically for DDG iterator
                    results = list(ddgs.text(query, max_results=5))
                    for r in results:
                        raw_leads.append({
                            "name": r.get("title"),
                            "website": r.get("href"),
                            "snippet": r.get("body"),
                            "source": "ddg_search"
                        })
            except Exception as e:
                print(f"⚠️ [NEURAL] Search failed for {city}: {e}")
                raw_leads = MOCK_LEADS.get(niche, [])
        else:
            raw_leads = MOCK_LEADS.get(niche, [])

        # 2. ANALYSIS PHASE
        for lead in raw_leads:
            score = 50 # Default
            reason = "Heuristic baseline."
            
            # Prepare Lead Object
            display_name = lead.get("name", "Unknown Business")
            website = lead.get("website", "")
            snippet = lead.get("snippet", "")
            phone = lead.get("phone", "") 

            # LLM Scoring
            if model and (website or snippet):
                prompt = f"""
                Analyze this business lead for a marketing agency selling AI automation.
                Business: {display_name}
                Website: {website}
                Context: {snippet}

                Return a valid JSON object ONLY with:
                - score (0-100): High score if good candidate.
                - reason: Short explanation.
                """
                try:
                    res = model.generate_content(prompt)
                    txt = res.text.strip().replace("```json", "").replace("```", "")
                    if "{" in txt:
                        analysis = json.loads(txt[txt.find("{"):txt.rfind("}")+1])
                        score = analysis.get("score", 50)
                        reason = analysis.get("reason", "AI Analysis")
                except Exception as e:
                    print(f"⚠️ [NEURAL] AI Analysis failed: {e}")
            
            # 3. SAVE PHASE
            # Schema requires ghl_contact_id (NOT NULL) and website_url (not website)
            # We generate a temp ghl_id for new prospects
            import uuid
            temp_ghl_id = f"neural_{uuid.uuid4().hex[:12]}"
            
            db_record = {
                "ghl_contact_id": temp_ghl_id,
                "full_name": display_name,         # Schema uses full_name, we map company name here
                "website_url": website,            # Schema uses website_url
                "lead_score": score,
                "ai_strategy": f"Neural Reason: {reason}", # Map reason to ai_strategy
                "status": "new",
                "raw_research": {
                    "source": "neural_prospector",
                    "city": city,
                    "niche": niche,
                    "snippet": snippet
                }
            }
            if phone:
                db_record["phone"] = phone

            try:
                # Upsert based on ghl_contact_id (effectively valid since we generate it)
                # Note: Real dedupe logic needs to check existing names/websites first
                supabase.table("contacts_master").insert(db_record).execute()
                print(f"✅ [SAVED] {display_name} (Score: {score})")
                total_leads += 1
            except Exception as e:
                print(f"❌ [DB ERROR] Failed to save {display_name}: {e}")

    return {"status": "success", "leads_found": total_leads}

# Modal App Definition - Conditional
IF_MODAL = os.environ.get("MODAL_RUNTIME") or ("modal" in sys.modules and __name__ != "__main__")

if IF_MODAL:
    app = modal.App("v2-neural-prospector")
    VAULT = modal.Secret.from_name("agency-vault")

    @app.function(
        image=image, 
        secrets=[VAULT], 
        timeout=600,
        keep_warm=1
    )
    async def neural_hunt(niche: str, cities: List[str]):
        return await run_neural_hunt(niche, cities)
else:
    # Dummy for local import safety
    app = None
    async def neural_hunt(niche: str, cities: List[str]):
        return await run_neural_hunt(niche, cities)

# Local test hook
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # Load local env for testing
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.local")
    except: 
        pass
    
    # Run async test
    async def main():
        print("🧪 [TEST] Running Neural Prospector Locally...")
        await run_neural_hunt("emergency plumber", ["Miami"])
    
    asyncio.run(main())
