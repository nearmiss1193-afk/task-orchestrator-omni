"""
MISSION: RESEARCH WORKER - Hardened with Error Checks
Scrapes websites, analyzes with Gemini, dispatches email
"""
import sys
import os

if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT], timeout=300)
async def research_lead_logic(lead_id: str):
    """
    Researches a lead by ID (not full object - serialization fix).
    
    Args:
        lead_id: Database ID (not ghl_contact_id)
    """
    print(f"🕵️ RESEARCH START: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    import requests
    
    supabase = get_supabase()
    
    #  FETCH LEAD (with error check!)
    contact_res = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute()
    check_supabase_error(contact_res, "Fetch Lead")
    
    if not contact_res.data:
        raise Exception(f"Lead {lead_id} not found")
    
    lead = contact_res.data
    url = lead.get("website_url")
    
    if not url or url.strip() == "":
        print(f"⚠️ NO URL for {lead_id}, marking skipped")
        skip_res = supabase.table("contacts_master").update({"status": "skipped_no_url"}).eq("id", lead_id).execute()
        check_supabase_error(skip_res, "Mark Skipped")
        return {"error": "no_url"}
    
    # SCRAPE
    scraped_content = {}
    print(f"🌐 SCRAPING: {url}")
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            scraped_content["homepage"] = await page.inner_text()
            await browser.close()
            print("✅ PLAYWRIGHT SUCCESS")
    except Exception as e:
        print(f"⚠️ Playwright Fallback: {e}")
        try:
            scraped_content["homepage"] = requests.get(url, timeout=10).text[:10000]
            print("✅ REQUESTS FALLBACK SUCCESS")
        except Exception as e2:
            print(f"❌ SCRAPE FAILED: {e2}")
            scraped_content["homepage"] = "Content unavailable"
    
    # GEMINI ANALYSIS
    print("🧠 GEMINI START")
    from modules.ai.routing import get_gemini_model
    try:
        model = get_gemini_model("pro")
        prompt = f"Analyze this business for inefficiencies and write a casual outreach hook: {scraped_content['homepage'][:5000]}"
        res = model.generate_content(prompt)
        hook = res.text.strip()
        print(f"✅ GEMINI SUCCESS: {hook[:50]}...")
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        hook = "saw your site, had a quick question"
    
    # UPDATE DB (with error check!)
    print("💾 UPDATING DB...")
    update_res = supabase.table("contacts_master").update({
        "status": "research_done",
        "ai_strategy": hook
    }).eq("id", lead_id).execute()
    check_supabase_error(update_res, "Update Lead Status")
    print(f"✅ DB UPDATED: research_done")
    
    # Auto-dispatch email (pass ID only!)
    print("📧 AUTO-DISPATCHING EMAIL...")
    from workers.outreach import dispatch_email_logic
    dispatch_email_logic.spawn(lead_id)
    
    print("🏁 RESEARCH COMPLETE")
    return {"status": "ok", "lead_id": lead_id}
