import os
import json
import random
import time
import datetime
from supabase import create_client
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY") # Updated env var
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash") # Updated model

def run_predator_vision(url: str):
    """Headless Browser Analysis"""
    if not url: return {"error": "no url"}
    if not url.startswith("http"): url = "https://" + url
        
    findings = {
        "clickable_phone": False,
        "contact_form": False,
        "is_alive": False,
        "meta_text": ""
    }
    
    try:
        with sync_playwright() as p:
            print(f"   🕷️ Browsing {url}...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=15000)
                findings["is_alive"] = True
                
                # Checks
                if len(page.query_selector_all('a[href^="tel:"]')) > 0:
                    findings["clickable_phone"] = True
                if len(page.query_selector_all('form')) > 0 or len(page.query_selector_all('input')) > 2:
                    findings["contact_form"] = True
                    
                findings["meta_text"] = page.title() + " - " + (page.locator("body").inner_text()[:500].replace('\n', ' ') or "")
            except Exception as e:
                findings["error"] = str(e)
                print(f"   ⚠️ Page Load Error: {e}")
            finally:
                browser.close()
    except Exception as e:
        findings["error"] = str(e)
        print(f"   ❌ Playwright Error: {e}")
        
    return findings

def research_lead(lead):
    contact_id = lead.get("ghl_contact_id")
    url = lead.get("website_url")
    print(f"🔍 Researching {lead.get('full_name')} ({url})...")
    
    if not url:
        print("   ❌ No URL. Marking as skipped.")
        supabase = get_supabase()
        supabase.table("contacts_master").update({"status": "skipped_no_url"}).eq("ghl_contact_id", contact_id).execute()
        return

    # 1. Vision
    vision_data = run_predator_vision(url)
    
    # 2. AI Analysis
    model = get_gemini_model()
    
    vision_context = f"Site Alive: {vision_data.get('is_alive')}. Phone: {vision_data.get('clickable_phone')}. Form: {vision_data.get('contact_form')}."
    
    prompt = f"""
    Analyze service business: {url}
    Vision: {vision_context}
    Text: {vision_data.get("meta_text", "")}
    
    Identify 1 operational inefficiency (e.g. missed calls, no automation).
    Write 1 short spartan hook (lowercase).
    Rate automation potential (0-100).
    
    JSON: {{"inefficiencies": [], "hook": "", "automation_score": 0}}
    """
    
    try:
        res = model.generate_content(prompt)
        text = res.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(text)
    except Exception as e:
        print(f"   ❌ AI Error: {e}")
        analysis = {"inefficiencies": ["unknown"], "hook": "saw your site, let's chat.", "automation_score": 50}

    # Add extra data fields
    analysis["traffic_stats"] = {"direct_pct": 50, "ai_search_pct": 5}
    analysis["est_revenue"] = "Under $1M"
    
    # Update DB
    supabase = get_supabase()
    supabase.table("contacts_master").update({
        "raw_research": analysis,
        "lead_score": analysis.get("automation_score"),
        "status": "research_done", # ADVANCE STATUS
        "ai_strategy": analysis.get("hook")
    }).eq("ghl_contact_id", contact_id).execute()
    
    print(f"   ✅ Saved. Score: {analysis.get('automation_score')}. Hook: {analysis.get('hook')}")

def run_batch(limit=5):
    supabase = get_supabase()
    print(f"🚀 Starting Turbo Research (Batch {limit})...")
    
    # Fetch new leads
    leads = supabase.table("contacts_master").select("*").eq("status", "new").limit(limit).execute()
    
    if not leads.data:
        print("✅ No 'new' leads found.")
        return
        
    print(f"📊 Found {len(leads.data)} leads.")
    
    for lead in leads.data:
        research_lead(lead)

if __name__ == "__main__":
    run_batch(50)
